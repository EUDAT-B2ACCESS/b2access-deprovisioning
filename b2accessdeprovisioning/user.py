from __future__ import absolute_import


class User(object):

    def __init__(self, **kwargs):
        """ Constructs a new :class:`User <User>`.

        :param internal_id: user identifier internal to the IDM system.
        :param shared_id: user identifier shared with entities external
            to the IDM system
        """
        if 'internal_id' in kwargs:
            self.internal_id = kwargs['internal_id']
        if 'shared_id' in kwargs:
            self.shared_id = kwargs['shared_id']
        if 'email' in kwargs:
            self.email = kwargs['email']
