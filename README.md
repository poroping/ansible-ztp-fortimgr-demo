# ansible-ztp-fortimgr-demo

### Requirements
- FortiManager
- FortiGate (50x used in this example, 60x will error due to different interface naming)
- Staging network that can reach FortiManager
- Ansible >= 2.10
- Ansible galaxy FortiManager >= 2.0.1

https://ansible-galaxy-fortimanager-docs.readthedocs.io/en/galaxy-2.0.1/

---

DHCP server of staging network must include option240/241 pointing to IP/FQDN of FortiManager https://docs.fortinet.com/document/fortigate/6.2.0/cookbook/861490/zero-touch-provisioning-with-fortimanager

Debug command to see if DHCP option is working:

```diagnose fdsm fmg-auto-discovery-status```
```
FGT51E3U17001742 # diagnose fdsm fmg-auto-discovery-status
dhcp: fmg-ip=0.0.0.0, fmg-domain-name='f.sensa.is', config-touched=1(/bin/dhcpcd)
```
Note the ip/domain name is set and the config-touched flag is set. This means it will not attempt ZTP again, unless factory reset.

---

## Inventory

Modify your inventory file to point to your FortiManager. Make sure these credentials are temporary and the user locked down by trustedhosts. Secure credential storage is outside the scope of this demo.

```
[fortimanagers]
demo ansible_host=f.sensa.is ansible_user="demo" ansible_password="Z7PD3m0!!!"

[fortimanagers:vars]
ansible_network_os=fortinet.fortimanager.fortimanager
```

---
## The plays

```01_globals.yml```

This play adds some global meta fields we will use later, run it.

```02_stage_adom.yml```

This will add an ADOM and configure the ADOM objects we will use to configure the device we are provisioning. This rabbit hole we won't go down too far, just run this for now.
- Add ADOM w/ custom meta field populated (in this case the national business ID number)
- Add dynamic interfaces
- Configure firewall policy on default firewall policy package
- Add a script that we will run against the device database to change the admin password

```03_stage_device_basic.yml```

**Change serial number if you're playing along at home**

This play will add a device and set the required flags for the device to connect and pull it's configuration via ZTP. You can run this, modify the device config manually, apply policy packages etc. Then when you are ready factory reset your FortiGate and plug into the staging network. If everything works it will boot, get IP and DHCP options, then reach out to the FortiManager. The FortiManager will show a task running by user "Auto link", it will setup it's config tunnel to the device and push out the config as per the FortiManager's device database.

Fun!

```04_stage_device_inter.yml```

**Again, change serial number if you're playing along at home**

This play will show you how you can fully automate the provisioning of a device via ZTP and FortiManager API.

*There is an assumption of basic Ansible knowledge here. We will focus on the Fortinet stuff.*

```roles/add-model-device/tasks/main.yml```

The first role is similar to the previous play and will add the device by serial and set the flags required. It also populates some of the meta fields.

```roles/config-model-device/tasks/main.yml```
```
- name: Setup internet1.
  fmgr_generic:

---omit---

- name: Setup default route.
  fmgr_generic:

---omit---

- name: Setup lan.
  fmgr_generic:
```
These generic modules are operating on the device database directly. Adding interfaces, dhcp and routing.

```
- name: Map internet interfaces.
  fmgr_dynamic_interface_dynamicmapping:

---omit---

- name: Map internal interfaces.
  fmgr_dynamic_interface_dynamicmapping:

```
This maps the device interfaces to dynamic (or normalised) interfaces we reference in ADOM level objects and policies.
```
- name: Run script.
  fmgr_dvmdb_script_execute:
```
This executes the chosen scripts against the device database.
```
- name: Assign policy package.
  fmgr_pm_pkg_adom:
```

This assigns the policy package we have configured on the ADOM to the device.
```
- name: Install policy package.
  fmgr_securityconsole_install_package:
```
Finally we install the policy package to the device. This will add the required configuration to the device database.

At this point we are ready to ZTP. Again, factory reset and plug into the staging network. The device should auto join and pull all of it's configuration. Depending on how fancy you get it could now be ready for deployment.

```05_true_zero_touch.yml```

This play is a basic example of how this could be implemented with a frontend and dynamically retrieve information at the time of provisioning. The idea here being that a technician can unbox a device, enter basic information into a provisioning portal, plug it into the provisioning network, get a coffee and come back to a full configured and ready to deploy firewall. No interaction with a Network Engineer required.

Enter the frontend dir, install the required python modules and launch our super basic flask app.

```
cd ./frontend/
pip3 install -r requirements.txt
python3 app.py
```

Navigate to http://localhost:5000/ and check the sweet formatting.

If you're playing along at home, delete your test device from the FortiManager and enter your device ```serial number``` in the Serial field, line number for this example is ```ns-1234``` and select ```FISH``` as your customer.

On form submission the device will be provisioned on FortiManager and the physical device can be (factory reset) and connected to the staging network. ZTP will trigger and the device will pull it's full configuration from the FortiManager.

We achieve this dynamically by having the play retrieve the required device variables from our "database" (http://localhost:5000/json).

Hope this demo helps anyone interested in implementing FortiZTP deployments.

**FIN**

---
---

I have an old working POC for a full setup with validation and logic and including staging FortiSwitch and FortiAPs but need to dust it off and get it working again. If anyone is interested HMU.