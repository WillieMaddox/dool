### Authority: dag@wieers.com

### For more information, see:
###     http://eaglet.rain.com/rick/linux/schedstat/

class dstat_topcputime(dstat):
    """
    Name and total amount of CPU time consumed in milliseconds of the process
    that has the highest total amount of cputime for the measured timeframe.
    """

    def __init__(self):
        self.name = 'highest total'
        self.type = 's'
        self.width = 17
        self.scale = 0
        self.vars = ('cputime process',)
        self.pid = str(os.getpid())
        self.pidset1 = {}; self.pidset2 = {}
        info(1, 'Module dstat_topcputime is still experimental.')

    def check(self):
        if not os.access('/proc/self/schedstat', os.R_OK):
            raise Exception, 'Kernel has no scheduler statistics, use at least 2.6.12'

    def extract(self):
        self.val['result'] = 0
        self.val['process'] = ''
        for pid in os.listdir('/proc/'):
            try:
                ### Is it a pid ?
                int(pid)

                ### Filter out dstat
                if pid == self.pid: continue

                ### Reset values
                if not self.pidset1.has_key(pid):
                    self.pidset1[pid] = {'run_ticks': 0}

                ### Extract name
                name = open('/proc/%s/stat' % pid).read().split()[1][1:-1]

                ### Extract counters
                l = open('/proc/%s/schedstat' % pid).read().split()

            except ValueError:
                continue
            except IOError:
                continue

            if len(l) != 3: continue

            self.pidset2[pid] = {'run_ticks': long(l[0])}

            totrun = (self.pidset2[pid]['run_ticks'] - self.pidset1[pid]['run_ticks']) * 1.0 / elapsed

            ### Get the process that spends the most jiffies
            if totrun > self.val['result']:
                self.val['result'] = totrun
                self.val['pid'] = pid
                self.val['name'] = getnamebypid(pid, name)

        if step == op.delay:
            for pid in self.pidset2.keys():
                self.pidset1[pid].update(self.pidset2[pid])

        if self.val['result'] != 0.0:
            self.val['cputime process'] = '%-*s%s' % (self.width-4, self.val['name'][0:self.width-4], cprint(self.val['result'], 'f', 4, 100))

        ### Debug (show PID)
#       self.val['cputime process'] = '%*s %-*s' % (5, self.val['pid'], self.width-6, self.val['name'])

    def showcsv(self):
        return '%s / %.4f' % (self.val['name'], self.val['result'])

# vim:ts=4:sw=4:et