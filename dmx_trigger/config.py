#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DMX Video Trigger config file loading utility functions
"""

__author__ = "Pau Aliagas <linuxnow@gmail.com>"
__copyright__ = "Copyright (c) 2021 Pau Aliagas"
__license__ = "GPL 3.0"
__all__ = ['load_config']


import logging, logging.config, logging.handlers
import os
import warnings
import yaml


def load_config(filename, section=None):
    """
    Load a yaml configuration file.

    * Template rules for string interpolation can be used by the application
    * it adds vars to the environment, in uppercase
    * it configures the loggers

    It returns a dict with the whole config file or just the options defined in
    section if defined.

    :param str filename: a configuration file
    :param str section: an option section in the configuration file
    :return: a config dict with the options defined in section
    :rtype: dict
    """
    try:
        config = yaml.load(open(filename), Loader=yaml.SafeLoader)
    except IOError as e:
        raise Exception("non-existing config file '%s'" % filename)
    except yaml.YAMLError as e:
        raise yaml.YAMLError("invalid config file '%s'" % filename)

    # we should try to set up the environment as soon as possible
    if 'environment' in config:
        env_config = config.get('environment')
        for env_var, env_val in env_config.items():
            # in the environment, keys are generally upper case
            os.environ[env_var.upper()] = env_val

    # use whole file or just given section
    if section in config:
        section_config = config.get(section)
    else:
        # or leave the whole file as the default section
        section_config = config

    # logging should be configured before using it
    # logging config comes from a separate file or from the same file
    # it can be configured in the given section or at root level
    loggers = logconfig = None
    if 'loggers' in section_config:
        loggers = section_config.get('loggers')
    elif 'loggers' in config:
        loggers = config.get('loggers')
    else:
        loggers = None
    # now choose 1st config, then file
    if loggers:
        # first embedded config
        if 'config' in loggers:
            logconfig = loggers.get('config')
        elif 'file' in loggers:
            # load yaml logconfig file 1st, then old ini format
            logfile = loggers.get('file')
            try:
                logconfig = yaml.load(open(logfile))
            except yaml.YAMLError as e:
                # try old ini format
                logconfig = None
                logging.config.fileConfig(logfile)
            except IOError as e:
                raise Exception("non-existing loconfig file '%s'" % logfile)
            except Exception as e:
                raise Exception("invalid config file '%s'" % logfile)
        else:
            logconfig = None
    # now load the configuration
    if logconfig:
        # Try to setup logging using the same config file
        try:
            logging.config.dictConfig(logconfig)
        except Exception as e:
            warnings.warn('logging could not be configured: %s' % e)
    else:
        # add a default null logger to avoid warnings
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    return section_config
