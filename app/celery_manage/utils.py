from app.models import Hosts, System, Disks
from app import db

class UpdateHosts:
    def __init__(self, data):
        '''
        data: {
                'hostname': '',
                'memory': '',
                'cpus': '',
                'disks': [{'name':'', 'size':''}, {}],
                'system': '',
                'local_ip': ''}
        '''
        self.data = data
        self.host = self._host()
        self.UpCpuMemHostname()
        self.UpDisk()
        self.UpSystem()

    def _host(self):
        local_ip = self.data.get('local_ip')
        host = Hosts.query.filter_by(local_ip=local_ip).first()
        return host

    def UpCpuMemHostname(self):
        self.host.hostname = self.data.get('hostname')
        self.host.cpus = self.data.get('cpus')
        self.host.memory = self.data.get('memory')

    def UpDisk(self):
        disks = self.data.get('disks')
        disknames = [ d.get('name') for d in self.data.get('disks') ]
        hostdisks = [ disk.diskname for disk in self.host.disk.all() ]
        
        havedisk = list(set(hostdisks) & set(disknames))
        deldisks = list(set(hostdisks) - set(disknames))
        addisks = list(set(disknames) - set(hostdisks))

        if havedisk:
            for diskname in havedisk:
                disk = Disks.query.filter_by(diskname=diskname).first()
                for d in disks:
                    if diskname == d.get('name'):
                        size = d.get('size')
                disk.size = size

        if deldisks:
            for diskname in deldisks:
                disk = Disks.query.filter_by(diskname=diskname).first()
                db.session.delete(disk)

        if addisks:
            for diskname in addisks:
                for d in disks:
                    if diskname == d.get('name'):
                        size = d.get('size')
                disk = Disks(diskname=diskname, size=size)
                db.session.add(disk)
                self.host.disk.append(disk)

    def UpSystem(self):
        sys = System.query.filter_by(name=self.data.get('system')).first()
        if not sys:
            sys = System(name=self.data.get('system'))
        self.host.systems = sys

    def __del__(self):
        db.session.commit()

