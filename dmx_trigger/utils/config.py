# -*- coding: UTF-8 -*-
"""
The DMX Trigger configuration utility functions
"""

def check_mandatory_keys(config, section, keys):
    """Check that mandatory keys are present in config

    :param dict config: the dictionary containing the configuration
    :param string section: the section in which to check for the keys
    :param list keys: the keys to check for existence
    :return: True
    :rtype: bool
    :raises KeyError: when there's some key missing
    """
    if not section in config:
        raise KeyError("No '%s' section provided in config file" % section)
    for name in keys:
        if name not in config[section]:
            raise KeyError("No '%s' found in section '%s'" % (name, section))
    return True

