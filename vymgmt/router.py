# Copyright (c) 2016 Hochikong

import re

from pexpect import pxssh


class VyOSError(Exception):
    pass


class ConfigError(VyOSError):
    pass


class CommitError(ConfigError):
    pass


class ConfigLocked(CommitError):
    pass


class Router(object):
    def __init__(self, address, user, password):
        """Initial a router object

        :param address: Router address,example:'192.168.10.10'
        :param cred: Router user and password,example:'vyos:vyos'
        """
        self.__address = address
        self.__user = user
        self.__password = password

        # Session flags
        self.__logged_in = False
        self.__session_modified = False
        self.__session_saved = True
        self.__conf_mode = False

        self.__conn = pxssh.pxssh()

        # String codec, hardcoded for now
        self.__codec = "utf8"

    def __execute_command(self, command):
        """This method used for sending configuration to VyOS

        :param obj: A connection object
        :param config: A configuration string
        :return: A message or an error
        """
        self.__conn.sendline(command)

        if not self.__conn.prompt():
            raise VyOSError("Connection timed out")

        output = self.__conn.before

        # XXX: In python3 it's bytes rather than str
        if isinstance(output, bytes):
            output = output.decode(self.__codec)
        return output

    def _status(self):
        """Check the router object inner status

        :return: A python dictionary include the status of the router object
       	"""
        return { "logged_in": self.__logged_in,
                 "session_modified": self.__session_modified,
                 "session_saved": self.__session_saved,
                 "conf_mode": self.__conf_mode }

    def login(self):
        """Login the router

        """
        self.__conn.login(self.__address, self.__user, self.__password)
        self.__logged_in = True

    def logout(self):
        """Logout the router

        :return: A message or an error
        """

        if not self.__logged_in:
            raise VyOSError("Not logged in")
        else:
            if self.__conf_mode:
                raise VyOSError("Cannot logout before exiting configuration mode")
            else:
                self.__conn.close()
                self.__logged_in = False

    def configure(self):
        """Enter the VyOS configure mode

        """
        if not self.__logged_in:
            raise VyOSError("Cannot enter configuration mode when not logged in")
        else:
            if self.__conf_mode:
                raise VyOSError("Session is already in configuration mode")
            else:
                # configure changes the prompt (from $ to #), so this is
                # a bit of a special case, and we use pxssh directly instead
                # of the __execute_command wrapper...
                self.__conn.sendline("configure")

                # XXX: set_unique_prompt() after this breaks things, for some reason
                # We should find out why.
                self.__conn.PROMPT = "[#$]"

                if not self.__conn.prompt():
                    raise VyOSError("Entering configure mode failed (possibly due to timeout)")

                #self.__conn.set_unique_prompt()
                self.__conf_mode = True

                # XXX: There should be a check for operator vs. admin
                # mode and appropriate exception, but pexpect doesn't work
                # with operator's overly restricted shell...

    def commit(self):
        """Commit the configuration changes

        """
        if not self.__conf_mode:
            raise VyOSError("Cannot commit without entering configuration mode")
        else:
            if not self.__session_modified:
                raise ConfigError("No configuration changes to commit")
            else:
                output = self.__execute_command("commit")

                if re.search(r"Commit\s+failed", output):
                    raise CommitError(output)
                if re.search(r"another\s+commit\s+in\s+progress", output):
                    raise ConfigLocked("Configuration is locked due to another commit in progress")

                self.__session_modified = False
                self.__session_saved = False

    def save(self):
        """Save the configuration after commit

        """
        if not self.__conf_mode:
            raise VyOSError("Cannot save when not in configuration mode")
        elif self.__session_modified:
            raise VyOSError("Cannot save when there are uncommited changes")
        else:
            self.__execute_command("save")
            self.__session_saved = True


    def exit(self, force=False):
        """Exit VyOS configure mode

        :param force: True or False
        """
        if not self.__conf_mode:
            pass
        else:
            # XXX: would be nice to simplify these conditionals
            if self.__session_modified:
                if not force:
                    raise VyOSError("Cannot exit a session with uncommited changes, use force flag to discard")
                else:
                    self.__execute_command("exit discard")
                    self.__conf_mode = False
                    return
            elif (not self.__session_saved) and (not force):
                raise VyOSError("Cannot exit a session with unsaved changes, use force flag to ignore")
            else:
                self.__execute_command("exit")
                self.__conf_mode = False

    def set(self, path):
        """Basic 'set' method,execute the set command in VyOS

        :param config: A configuration string.
                       e.g. 'protocols static route ... next-hop ... distance ...'
        """
        if not self.__conf_mode:
            raise ConfigError("Cannot execute set commands when not in configuration mode")
        else:
            output = self.__execute_command("{0} {1}". format("set", path))
            if re.search(r"Set\s+failed", output):
                raise ConfigError(output)
            elif re.search(r"already exists", output):
                raise ConfigError("Configuration path already exists")
            self.__session_modified = True

    def delete(self, path):
        """Basic 'delete' method,execute the delete command in VyOS

        :param path: A configuration string.
                               e.g. 'protocols static route ... next-hop ... distance ...'
        """
        if not self.__conf_mode:
            raise ConfigError("Cannot execute delete commands when not in configuration mode")
        else:
            output = self.__execute_command("{0} {1}". format("delete", path))
            if re.search(r"Nothing\s+to\s+delete", output):
                raise ConfigError(output)
            self.__session_modified = True
