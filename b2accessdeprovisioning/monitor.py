from __future__ import absolute_import

import json
import logging

from datetime import timedelta, datetime

import unityapiclient
from unityapiclient.client import UnityApiClient

from b2accessdeprovisioning.configparser import config
from b2accessdeprovisioning.user import User
from b2accessdeprovisioning.notifier import MailNotifier
import b2accessdeprovisioning.util as util

DEFAULT_API_PATH = 'rest-admin'
DEFAULT_API_VERSION = 'v1'
DEFAULT_API_CERT_VERIFY = True
DEFAULT_ATTR_WHITELIST = []
DEFAULT_RETENTION_PERIOD = 365
DEFAULT_NOTIFICATION_EMAIL_HOST = 'localhost'
DEFAULT_NOTIFICATION_EMAIL_PORT = 25
DEFAULT_NOTIFICATION_EMAIL_USE_TLS = False
DEFAULT_NOTIFICATION_EMAIL_SUBJECT = 'Deprovisioned B2ACCESS accounts'
DEFAULT_NOTIFICATION_EMAIL_INTRO_TEXT = 'See attachment for details of deprovisioned B2ACCESS accounts.\n\nNote: This is an automated email, please don\'t reply.'
DEFAULT_LOG_LEVEL = 'WARNING'
DEFAULT_DRY_RUN = False

logger = logging.getLogger(__name__)
logging.basicConfig(level=(logging.getLevelName(util.safeget(config, 'log_level')) or DEFAULT_LOG_LEVEL))

b2access = UnityApiClient(
    config['api']['base_url'],
    rest_admin_path=(util.safeget(config, 'api', 'path') or DEFAULT_API_PATH),
    api_version=(util.safeget(config, 'api', 'version') or DEFAULT_API_VERSION),
    auth=(config['api']['user'], config['api']['password']),
    cert_verify=(util.safeget(config, 'api', 'cert_verify') or DEFAULT_API_CERT_VERIFY))

notifier = MailNotifier(
    host=(util.safeget(config, 'notifications', 'email', 'host') or DEFAULT_NOTIFICATION_EMAIL_HOST),
    port=(util.safeget(config, 'notifications', 'email', 'port') or DEFAULT_NOTIFICATION_EMAIL_PORT),
    use_tls=(util.safeget(config, 'notifications', 'email', 'use_tls') or DEFAULT_NOTIFICATION_EMAIL_USE_TLS),
    user=util.safeget(config, 'notifications', 'email', 'user'),
    password=util.safeget(config, 'notifications', 'email', 'password'))

dry_run = (util.safeget(config, 'dry_run') or DEFAULT_DRY_RUN)

email_from = config['notifications']['email']['from']
email_to = config['notifications']['email']['to']


def main():
    groups = b2access.get_group()
    users = []
    for member_id in groups['members']:
        entity = b2access.get_entity(member_id)
        if entity['entityInformation']['state'] != 'disabled':
            continue
        if entity['entityInformation']['scheduledOperation'] == 'REMOVE':
            continue
        user = User(internal_id=member_id)
        users.append(user)
        for identity in entity['identities']:
            if identity['typeId'] == 'persistent':
                user.shared_id = identity['value']
                break

    for user in users:
        _remove_user_attrs(user)
        _schedule_user_removal(user)
        
    if users:
        _send_notification(users)


def _remove_user_attrs(user):
    attr_whitelist = (util.safeget(config, 'attr_whitelist') or DEFAULT_ATTR_WHITELIST)

    attrs = b2access.get_entity_attrs(user.internal_id, effective=False)
    for attr in attrs:
        if ('name' in attr and attr['name'] not in attr_whitelist and
            attr['visibility'] == 'full'):
            logger.debug("removing attribute '%s' from entity '%s'",
                        attr['name'], user.internal_id)
            if not dry_run:
                b2access.remove_entity_attr(user.internal_id, attr['name'], attr['email'])


def _schedule_user_removal(user):
    when = datetime.utcnow() + timedelta(days=(util.safeget(config, 'retention_period') or DEFAULT_RETENTION_PERIOD))
    logger.debug("scheduling removal of entity '%s' at '%s'",
                user.internal_id, when)
    if not dry_run:
        b2access.schedule_operation(user.internal_id, operation='REMOVE',
                                    when=when)


def _send_notification(users=[]):
    account_details = []
    for user in users:
        if user.shared_id is not None:
            account_details.append({'id': user.shared_id})
    if not account_details:
        return
    attachments = []
    attachment = {}
    attachment['filename'] = 'users.json'
    attachment['message'] = json.dumps(account_details, sort_keys=True,
                                       indent=4, separators=(',', ': '))
    attachments.append(attachment)
    logger.debug("sending email notification from address '%s' to '%s' "
        "with subject '%s' and attachment users.json:\n%s",
                email_from,
                email_to,
                (util.safeget(config, 'notifications', 'email', 'subject') or DEFAULT_NOTIFICATION_EMAIL_SUBJECT),
                attachment['message'])
    if not dry_run:
        notifier.send(email_from, 
                  email_to,
                  (util.safeget(config, 'notifications', 'email', 'subject') or DEFAULT_NOTIFICATION_EMAIL_SUBJECT),
                  (util.safeget(config, 'notifications', 'email', 'intro_text') or DEFAULT_NOTIFICATION_EMAIL_INTRO_TEXT),
                  attachments)


if __name__ == "__main__":
    main()