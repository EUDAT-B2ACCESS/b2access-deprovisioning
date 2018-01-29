b2accessdeprovisioning
======================

.. image:: https://img.shields.io/pypi/v/b2accessdeprovisioning.svg
    :target: https://pypi.python.org/pypi/b2accessdeprovisioning

A Python tool for handling the (de)provisioning of B2ACCESS user accounts.

The b2accessdeprovisioning tool can be used to retrieve the list of permanently disabled B2ACCESS user accounts via Unity's Administration API. For each of the disabled accounts, the tool performs the following operations:

#. immediate removal of assigned attributes (excluding user identifiers)
#. scheduled removal of all account information after a given period of time

Finally, the tool sends a notification to one or more recipients containing the list of deprovisioned accounts.

Features
--------

* B2ACCESS integration via Unity's Administration API v1
* Attribute whitelisting to indicate information that should be saved when removing account data; otherwise the tool removes all attributes assigned to permanently disabled B2ACCESS user accounts
* Adjustable duration of time for which the records of deprovisioned users should be maintained
* Email notifications via SMTP containing deprovisioned account information in json format

Python version
--------------

Python 2.6 or 2.7 are fully supported.

Installation
------------

To install the tool, simply run:

.. code-block:: bash

    $ pip install b2accessdeprovisioning
    🍺

Third party libraries and dependencies
--------------------------------------

The following libraries will be installed when you install the client library:

* `PyYAML <https://github.com/yaml/pyyaml>`_
* `unityapiclient <https://github.com/EUDAT-B2ACCESS/unity-api-python-client>`_
* `pytz <https://github.com/newvem/pytz>`_
* `requests <https://github.com/kennethreitz/requests>`_

Configuration
-------------
Tool settings are adjustable via the ``config.yml`` configuration file.

Example ``config.yml``
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    # B2ACCESS API endpoint connection details
    api:
      base_url: "https://b2access.eudat.eu:8443"
      path: "rest-admin"
      version: "v1"
      user: "unity_user"
      password: "unity_password"
      cert_verify: True

    # List of attributes that should be saved when removing user information.
    # Attributes not listed here will be immediately removed upon user
    # deprovisioning.
    attr_whitelist: []

    # Duration of time for which the records of deprovisioned users should be
    # maintained (in days). After that period all information about the
    # deprovisioned users will be permanently removed.
    retention_period: 365

    # Notification settings
    notifications:
      email: 
        # SMTP host to connect to. Defaults to the local host if empty.
        host: "smtp.example.eu"
        # SMTP port to connect to. Defaults to the standard SMTP port (25) if empty.
        port: 587
        # Whether to put the SMTP connection in TLS. Defaults to False.
        use_tls: True
        # Login username/password if the SMTP server requires authentication;
        # otherwise empty.
        user: "smtp_user"
        password: "smtp_password"
        # Sender address
        from: "B2ACCESS Notifications <noreply@b2access.eudat.eu>"
        # List of recipient addresses
        to:
          - "SP1 Operator <admin@sp1.eudat.eu>"
          - "SP2 Operator <admin@sp2.eudat.eu>"
          - "SP3 Operator <admin@sp3.eudat.eu>"
        subject: "Deprovisioned B2ACCESS accounts"
        intro_text: "See attachment for details of deprovisioned B2ACCESS accounts.\n\nNote: This is an automated email, please don't reply."

    # (Optional) The group of users to check for disabled user accounts.
    # Defaults to the ROOT group
    #user_group: "testGroup"

    # Logging level: CRITICAL, ERROR, WARNING, INFO, or DEBUG. Defaults to WARNING.
    log_level: "WARNING"

    # Determines if changes will be made if needed
    dry_run: False
      
See also ``config.yml.example``.

Usage
-----

Simply run the ``b2accessdeprovisioning.monitor`` module:

.. code-block:: bash

    $ python -m b2accessdeprovisioning.monitor

Note: The tool will look for the ``config.yml`` configuration file in the current directory.

Example notification
^^^^^^^^^^^^^^^^^^^^

Information about the deprovisioned user accounts is sent via an email attachment in json format (``users.json``):

.. code-block:: json

    [
        {
            "email": [
                "email1@example.com"
            ],
            "id": "3f3d5b40-26ce-45db-808a-a5ca3a4e7515"
        },
        {
            "email": [
                "email2@example.com",
                "email3@example.com"
            ],
            "id": "663a5b04-62ec-9d3b-078b-546734ae5733"
        },
        {
            "email": null,
            "id": "983d5b41-abdg-45dc-808b-64633a4e7516"
        }
    ]

Run on background
-----------------
In order to run the script on background, you need to create a job schedule. This cron command runs the script every 24th hour.

.. code-block:: bash

    $ 0 */24 * * * cd <path-to-repo> && python -m b2accessdeprovisioning.monitor

Documentation
-------------

Documentation is available at http://eudat-b2access.github.io/b2access-deprovisioning 

License
-------

Licensed under the Apache 2.0 license, for details see `LICENSE`.
