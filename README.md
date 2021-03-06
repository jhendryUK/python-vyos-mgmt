#VyMGMT
A python library for VyOS configurations

This python library is used for VyOS configurations.  

Use this library to send the configuration commands to VyOS. 

##Note
###Version:0.1 
 
###Author:Hochikong  
 
###Contact me:hochikong@foxmail.com(usually use) or michellehzg@gmail.com(Inconvenient in Mainland China)  

###License:MIT   
  
###Requirement:pexpect(pxssh)  

###Platform:Python2 and 3

##Basic Example
Set a description for eth0:   

    >>> from vymgmt.router import Router
    >>> vyos = Router('192.168.225.2','vyos:vyos')
    >>> vyos.login()
    >>> vyos.configure()
    >>> vyos.set("interfaces ethernet eth0 description 'eth0'")
    >>> vyos.status()
    {'save': 'No', 'status': 'login', 'configure': 'Yes', 'commit': 'No'}
    >>> vyos.commit()
    >>> vyos.status()
    {'save': 'No', 'status': 'login', 'configure': 'Yes', 'commit': 'Yes'}
    >>> vyos.save()
    >>> vyos.status()
    {'save': 'Yes', 'status': 'login', 'configure': 'Yes', 'commit': 'Yes'}
    >>> vyos.exit()
    >>> vyos.logout()
    >>> vyos.status()
    {'save': None, 'status': 'logout', 'configure': None, 'commit': None}

Because we have save the configuration,so if you reboot the VyOS system but the static router still works.

If you change the configuration,you must commit and save it then you can exit configure mode.But you can use vyos.exit(force=Ture) to execute "exit discard" command. 

##Something you should know
1.Only admin level user can use this library to login and execute all configuration methods.  

2.When you initialize the Router class,the second parameters is 'username:password'.  

3.set() and delete() method is the core function of this library,you can just use a same configuration command on VyOS to set or delete a specify configuration.But you should take a look at the Basic Example and All Methods sections.  

#Quick Start
I will show you how to use this library to configuration the VyOS

The first step is login and configure a interface for management.Look at this example,in this example,I have configure eth0 for vymgmt,and I will show you how to login and configure an interface by this library。

Let's check the interfaces.Well,eth1 is the target interface,and we should set a address for this interface:

	vyos@vyos1:~$ show interfaces
	Codes: S - State, L - Link, u - Up, D - Down, A - Admin Down
	Interface        IP Address                        S/L  Description
	---------        ----------                        ---  -----------
	eth0             192.168.225.2/24                  u/u  
	eth1             -                                 u/u  
	eth2             192.168.83.142/24                 u/u  
	lo               127.0.0.1/8                       u/u  
	                 ::1/128

Let's import the Router and initialize a Router instance:
	
	>>> from vymgmt.router import Router
	>>> vyos1 = Router('192.168.225.2','vyos:vyos')

You should import class Router from vymgmt.router,the use address and "username:password" to initialize the instance.

Then,you can use login() to login vyos1:
	
	>>> vyos1.login()

If there are no problems,this method will return nothing to user.

By now,you can use configure() and execute configuration commands:

	>>> vyos1.configure()

You can use status() method to get the status of this instance:

	>>> vyos1.status()
	{'status': 'login', 'commit': None, 'save': None, 'configure': 'Yes'}

When you just initialize,all values are None.When you login,"status"'s value will change to "login"

But you can see "commit" and "save"'s value are None,because now we just login and enter configure mode.Now,the value of "configure" is "Yes".

Next,we can use set() to set a address for eth1:

	>>> vyos1.set("interfaces ethernet eth1 address '192.168.10.5'")
	Traceback (most recent call last):
	  File "<stdin>", line 1, in <module>
	  File "build/bdist.linux-x86_64/egg/vymgmt/router.py", line 218, in set
	vymgmt.base_exception.exceptions_for_set_and_delete.ConfigValueError: 
	set interfaces ethernet eth1 address '192.168.10.5'
	
	  Invalid IPv4 address/prefix
	  
	  Value validation failed
	  Set failed

Oh,NO!I just forgot the netmask.But you can see,if your input has mistakes,this library will raise a exception and display the error message to you.Because my configuration lost netmask,therefore the error reason is invalid address.And vymgmt will raise a ConfigValueError.You can see "Exceptions" section to get more information.

Now,let's use a correct configuration:

	>>> vyos1.set("interfaces ethernet eth1 address '192.168.10.5/24'")

Well,I have set the address for eth1 now.

Let's check the status now:

	>>> vyos1.status()
	{'status': 'login', 'commit': 'No', 'save': 'No', 'configure': 'Yes'}

You can see,"commit" and "save" are "No",so,you must commit and save it.

Commit:

	>>> vyos1.commit()

Save it:

	>>> vyos1.save()

Let's check the status again:

	>>> vyos1.status()
	{'status': 'login', 'commit': 'Yes', 'save': 'Yes', 'configure': 'Yes'}

You see,the value of "commit" and "save" have changed to "Yes",now I can exit the configure mode and logout.But if you don't commit and save,you still can use "vyos1.exit(force=True)" to exit and discard what you have configured:

	>>> vyos1.exit()
	>>> vyos1.logout()
	>>> vyos1.status()
	{'status': 'logout', 'commit': None, 'save': None, 'configure': None}

Now,I have configured an ethernet interface by this library,let's check it on vyos1:

	vyos@vyos1:~$ show interfaces
	Codes: S - State, L - Link, u - Up, D - Down, A - Admin Down
	Interface        IP Address                        S/L  Description
	---------        ----------                        ---  -----------
	eth0             192.168.225.2/24                  u/u  
	eth1             192.168.10.5/24                   u/u  
	eth2             192.168.83.142/24                 u/u  
	lo               127.0.0.1/8                       u/u  
	                 ::1/128

Now,I will show you how to use set() method to configure a rip router:

Topo:

	test1---VyOS1———VyOS2---test3

The address of test1 is 192.168.225.3,and the address of test3 is 192.168.157.8.Now these two vms can not ping each other.

	root@test1:~# ping -c 5 192.168.157.8
	PING 192.168.157.8 (192.168.157.8) 56(84) bytes of data.

	--- 192.168.157.8 ping statistics ---
	5 packets transmitted, 0 received, 100% packet loss, time 4017ms

I have set two test vms' gateway.Now login vyos1,configure the rip network:

	>>> from vymgmt.router import Router
	>>> vyos1 = Router('192.168.225.2','vyos:vyos')
	>>> vyos1.login()
	>>> vyos1.configure()

First,we should add a new lo address:

	>>> vyos1.set("interfaces loopback lo address 1.1.1.1/32")

Then configure rip networks:

	>>> vyos1.set("protocols rip network 192.168.225.0/24")
	>>> vyos1.set("protocols rip network 192.168.10.0/24")

And the last step:

	>>> vyos1.set("protocols rip redistribute connected")

Sometimes,you may forget to commit or save,the library will raise an exception and refuse to exit:

	>>> vyos1.status()
	{'status': 'login', 'commit': 'No', 'save': 'No', 'configure': 'Yes'}
    >>> vyos1.exit()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "build/bdist.linux-x86_64/egg/vymgmt/router.py", line 233, in exit
    vymgmt.base_exceptions.base.MaintenanceError: 
    Error : You should commit first.
	>>> vyos1.save()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "build/bdist.linux-x86_64/egg/vymgmt/router.py", line 185, in save
    vymgmt.base_exceptions.base.MaintenanceError: 
    Error : You need to commit first!

Therefore,we should execute commit() and save():

	>>> vyos1.commit()
	>>> vyos1.save()

Then on vyos2,we can configure rip network:

	>>> vyos2 = Router('192.168.10.6','vyos:vyos')
	>>> vyos2.login()
	>>> vyos2.configure()
	>>> vyos2.set("protocols rip network 192.168.10.0/24")
	>>> vyos2.set("protocols rip network 192.168.157.0/24")
	>>> vyos2.set("protocols rip redistribute connected")
	>>> vyos2.commit()
	>>> vyos2.save()

Then check it on test1:

	root@test1:~# ping 192.168.157.8 -c 5
	PING 192.168.157.8 (192.168.157.8) 56(84) bytes of data.
	64 bytes from 192.168.157.8: icmp_seq=1 ttl=62 time=0.947 ms
	64 bytes from 192.168.157.8: icmp_seq=2 ttl=62 time=1.12 ms
	64 bytes from 192.168.157.8: icmp_seq=3 ttl=62 time=1.34 ms
	64 bytes from 192.168.157.8: icmp_seq=4 ttl=62 time=1.37 ms
	64 bytes from 192.168.157.8: icmp_seq=5 ttl=62 time=1.48 ms

	--- 192.168.157.8 ping statistics ---
	5 packets transmitted, 5 received, 0% packet loss, time 4009ms
	rtt min/avg/max/mdev = 0.947/1.255/1.482/0.196 ms

On test3:

	root@test3:~# ping 192.168.225.3 -c 5
	PING 192.168.225.3 (192.168.225.3) 56(84) bytes of data.
	64 bytes from 192.168.225.3: icmp_seq=1 ttl=62 time=1.18 ms
	64 bytes from 192.168.225.3: icmp_seq=2 ttl=62 time=1.38 ms
	64 bytes from 192.168.225.3: icmp_seq=3 ttl=62 time=1.25 ms
	64 bytes from 192.168.225.3: icmp_seq=4 ttl=62 time=1.35 ms
	64 bytes from 192.168.225.3: icmp_seq=5 ttl=62 time=1.03 ms

	--- 192.168.225.3 ping statistics ---
	5 packets transmitted, 5 received, 0% packet loss, time 4008ms
	rtt min/avg/max/mdev = 1.036/1.241/1.381/0.127 ms

Now,maybe you are understand how to use this library to configure VyOS. 
 
#All Methods
##status():
Check the router object inner status.  

Return a dictionary include the status of BasicRouter instance.  

##login():
Login the VyOS system when you have create a new BasicRouter instance.  

##logout()
Logout the VyOS system.  

This method execute a close() on a connection.  

You can use this method logout a router substance.After logout,you can use the same instance to login again.  

##configure()
Enter the VyOS configure mode  

You must login the VyOS system before use this method.  

##commit()
Commit the configuration changes.  

You can use this method to commit your configuration.  

Due to configuration methods will change the value of the keys in self.__status.You should commit the configurations then can you save or exit.  

##save()
Save the configuration after commit.  

You can use this method to save your configuration.  

##exit(force=False)
Exit VyOS configure mode.  
If you not use "force",you can exit without save but you should commit first or it will raise a exception  

Example:  
force: True or False  

If force=True,this method will execute "exit discard" command and all your changes will lost.  

##set(config)
Basic 'set' method,execute the set command in VyOS.

Example:  
config: "interfaces ethernet eth0 description 'eth0'"

The minimal configuration method.

##delete(config)
Basic 'delete' method,execute the delete command in VyOS.

Example:  
config: "interfaces ethernet eth0 description 'eth0'"

The minimal configuration method.

#Exceptions
##vymgmt.base\_exceptions.exceptions\_for\_commit.CommitFailed()

This exception class is for commit() failures due to some mistakes in your configurations.  

When this exception raise,the error message from VyOS will displayed.

##vymgmt.base\_exceptions.exceptions\_for\_commit.CommitConflict()

This exception class is for commit() failures due to the commit conflicts when more than one users committing their configurations at the same time.

When this exception raise,the error message from VyOS will displayed.
 
##vymgmt.base\_exceptions.exceptions\_for\_set\_and\_delete.ConfigPathError()

This exception class is for set() and delete() failures due to configuration path error.  

What is configuration path error?

This configuration is correct:

	vyos.set("protocols rip network xxx")

This is wrong:

	vyos.delete("ethernet interface eth1 address")

The wrong one will raise this exception and display the error message:

	Configuration path: [ethernet] is not valid
  	Delete failed

When this exception raise,the error message from VyOS will displayed.

##vymgmt.base\_exceptions.exceptions\_for\_set\_and\_delete.ConfigValueError()

This exception class is for set() and delete() failures due to value error.  

This exception will raise when your configuration has wrong value,such as:

	vyos.set("interfaces ethernet eth1 address '192.168.225.2")   #No netmask

When this exception raise,the error message from VyOS will displayed.

##vymgmt.base_exceptions.CommonError()

This exception class is for all failures which do not covered by exceptions above.

When this exception raise,the error message from VyOS will displayed. 

##vymgmt.base_exceptions.MaintenanceError()

This exception class is for all maintenance method such login(),logout(),configure() has errors.

When this exception raise,the error message from VyOS will displayed. 




