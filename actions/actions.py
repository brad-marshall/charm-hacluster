#!/usr/bin/python
#
# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
sys.path.append('hooks/')
from charmhelpers.core.hookenv import log, action_set, action_fail

import xml.etree.ElementTree as ET

from subprocess import check_output, CalledProcessError

from utils import (
    pause_unit,
    resume_unit,
)


def pause(args):
    """Pause the hacluster services.
    @raises Exception should the service fail to stop.
    """
    pause_unit()


def resume(args):
    """Resume the hacluster services.
    @raises Exception should the service fail to start."""
    resume_unit()

def cleanup(args):
    """Cleans up any clonesets"""
    try:
        out = check_output(['crm', 'configure', 'show', 'xml']).decode('UTF-8')
    except CalledProcessError as e:
        log(e)
        action_fail("crm config show failed with error: {}".format(e.message))

    root = ET.fromstring(out)

    for clone in root.findall('./configuration/resources/clone/primitive'):
        str = "crm resource cleanup %s" % (clone.attrib['id'])
        cmd = str.split()
        try:
            cleanup = check_output(cmd).decode('UTF-8')
            action_set({'message': cleanup})
        except CalledProcessError as e:
            log(e)
            action_fail("crm cleanup failed with error: {}".format(e.message))


ACTIONS = {"pause": pause, "resume": resume, "cleanup": cleanup}


def main(args):
    action_name = os.path.basename(args[0])
    try:
        action = ACTIONS[action_name]
    except KeyError:
        return "Action %s undefined" % action_name
    else:
        try:
            action(args)
        except Exception as e:
            action_fail(str(e))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
