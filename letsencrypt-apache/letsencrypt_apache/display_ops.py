"""Contains UI methods for Apache operations."""
import logging
import os

import zope.component

from letsencrypt import interfaces

import letsencrypt.display.util as display_util


logger = logging.getLogger(__name__)


def select_vhost(domain, vhosts):
    """Select an appropriate Apache Vhost.

    :param vhosts: Available Apache Virtual Hosts
    :type vhosts: :class:`list` of type `~obj.Vhost`

    :returns: VirtualHost or `None`
    :rtype: `~obj.Vhost` or `None`

    """
    if not vhosts:
        return None
    while True:
        code, tag = _vhost_menu(domain, vhosts)
        if code == display_util.HELP:
            _more_info_vhost(vhosts[tag])
        elif code == display_util.OK:
            return vhosts[tag]
        else:
            return None


def _vhost_menu(domain, vhosts):
    """Select an appropriate Apache Vhost.

    :param vhosts: Available Apache Virtual Hosts
    :type vhosts: :class:`list` of type `~obj.Vhost`

    :returns: Display tuple - ('code', tag')
    :rtype: `tuple`

    """
    # Free characters in the line of display text (9 is for ' | ' formatting)
    # Additional characters are necessary for box formatting
    free_chars = display_util.WIDTH - len("HTTPS") - len("Enabled") - 9 - 6

    if free_chars < 2:
        logger.debug("Display size is too small for "
                     "letsencrypt_apache.display_ops._vhost_menu()")
        # This runs the edge off the screen, but it doesn't cause an "error"
        filename_size = 1
        disp_name_size = 1
    else:
        # Filename is a bit more important and probably longer with 000-*
        filename_size = int(free_chars * .6)
        disp_name_size = free_chars - filename_size

    choices = []
    for vhost in vhosts:
        if len(vhost.get_names()) == 1:
            disp_name = next(iter(vhost.get_names()))
        elif len(vhost.get_names()) == 0:
            disp_name = ""
        else:
            disp_name = "Multiple Names"

        choices.append(
            "{fn:{fn_size}s} | {name:{name_size}s} | {https:5s} | "
            "{active:7s}".format(
                fn=os.path.basename(vhost.filep)[:filename_size],
                name=disp_name[:disp_name_size],
                https="HTTPS" if vhost.ssl else "",
                active="Enabled" if vhost.enabled else "",
                fn_size=filename_size,
                name_size=disp_name_size)
        )

    code, tag = zope.component.getUtility(interfaces.IDisplay).menu(
        "We were unable to find a vhost with a ServerName or Address of {0}.{1}"
        "Which virtual host would you like to choose?".format(
            domain, os.linesep),
        choices, help_label="More Info", ok_label="Select")

    return code, tag


def _more_info_vhost(vhost):
    zope.component.getUtility(interfaces.IDisplay).notification(
        "Virtual Host Information:{0}{1}{0}{2}".format(
            os.linesep, "-" * (display_util.WIDTH - 4), str(vhost)),
        height=display_util.HEIGHT)
