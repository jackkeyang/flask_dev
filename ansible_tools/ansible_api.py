#!/usr/bin/python
#coding=utf8
import json
from collections import namedtuple
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
from ansible import context
import ansible.constants as C
import os

class ResultCallback(CallbackBase):
    def __init__(self):
        super(ResultCallback,self).__init__()
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_ok(self, result, **kwargs):
        self.host_ok[result._host] = result._result
#        host = result._host
#        print json.dumps({host.name: result._result}, indent=4)

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host] = result._result
#        host = result._host
#        print json.dumps({host.name: result._result}, indent=4)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.host_failed[result._host] = result._result
#        host = result._host
#        print json.dumps({host.name: result._result}, indent=4)

class Ansible_api:
    def __init__(self, hostlist=None):
        self.loader = DataLoader()
        self.variable_manager = VariableManager()
        self.inventory = InventoryManager(loader=self.loader, sources='%s,'%hostlist)
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        context.CLIARGS = ImmutableDict(connection='ssh', module_path=None, forks=10, become=None, timeout=30,
                                        become_method=None, become_user=None, check=False, diff=False)

    def run_adhoc(self, module, args, ansible_hosts):

        play_source = {
            "name": "ansible api run_adhoc",
            "hosts": ansible_hosts,
            "gather_facts": "no",
            "tasks": [
                {"action":{"module": module, "args": args}}
            ]
        }

        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        tqm = None
        try:
            results_callback = ResultCallback()
            tqm = TaskQueueManager(
                inventory = self.inventory,
                variable_manager = self.variable_manager,
                loader = self.loader,
                passwords = None,
                stdout_callback = results_callback,
            )
       
            tqm.run(play)
            return results_callback
        finally:
            if tqm is not None: 
                tqm.cleanup()

    def run_playbook(self, yaml_file_list, host):
        # 这里extra_vars作用是为playbook yml文件传变量
        self.variable_manager.extra_vars = {"host": host}
        pb = PlaybookExecutor(
            playbooks=yaml_file_list,
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            passwords = None,
            options=self.options
        )
        result = pb.run()
        print result

if __name__ == '__main__':
    #ansible_api = Ansible_api('172.16.10.11, 172.16.10.12')
    ansible_api = Ansible_api('172.16.10.11, 172.16.10.12, 172.16.10.13')
    #result = ansible_api.run_adhoc('ping', '','172.16.10.12')
    result = ansible_api.run_adhoc('setup', '', '172.16.10.11')
    for ip, data in result.host_ok.items():
        local_ip = ip
        info = data
        system = data.get('ansible_facts').get('ansible_os_family')
        mem = data.get('ansible_facts').get('ansible_memory_mb').get('real')
        cpus = data.get('ansible_facts').get('ansible_processor_cores')
        hostname = data.get('ansible_facts').get('ansible_fqdn')
        disks = []
        for name, info in data.get('ansible_facts').get('ansible_devices').items():
            if name.startswith('sd'):
                size = info.get('size')
                disks.append({'name': name, 'size': size})
        print system, disks, mem, hostname, cpus
