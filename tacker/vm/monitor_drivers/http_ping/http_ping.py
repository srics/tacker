#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import urllib2

from oslo_config import cfg

from tacker.common import log
from tacker.i18n import _LW
from tacker.openstack.common import log as logging
from tacker.vm.monitor_drivers import abstract_driver


LOG = logging.getLogger(__name__)
OPTS = [
    cfg.IntOpt('retry', default=5,
               help=_('number of times to retry')),
    cfg.IntOpt('timeout', default=1,
               help=_('number of seconds to wait for a response')),
    cfg.IntOpt('port', default=80,
               help=_('HTTP port number to send request'))
]
cfg.CONF.register_opts(OPTS, 'monitor_http_ping')


class VNFMonitorHTTPPing(abstract_driver.VNFMonitorAbstractDriver):
    def get_type(self):
        return 'http_ping'

    def get_name(self):
        return 'HTTP ping'

    def get_description(self):
        return 'Tacker HTTP Ping Driver for VNF'

    def monitor_url(self, plugin, context, device):
        LOG.debug(_('monitor_url %s'), device)
        return device.get('monitor_url', '')

    def _is_pingable(self, mgmt_ip='', retry=5, timeout=5, port=80, **kwargs):
        """Checks whether the server is reachable by using urllib2.

        Waits for connectivity for `timeout` seconds,
        and if connection refused, it will retry `retry`
        times.
        :param mgmt_ip: IP to check
        :param retry: times to reconnect if connection refused
        :param timeout: seconds to wait for connection
        :param port: port number to check connectivity
        :return: bool - True or False depending on pingability.
        """
        url = 'http://' + mgmt_ip + ':' + str(port)
        for retry_index in range(int(retry)):
            try:
                urllib2.urlopen(url, timeout=timeout)
                return True
            except urllib2.URLError:
                LOG.warning(_LW('Unable to reach to the url %s'), url)
        return 'failure'

    @log.log
    def monitor_call(self, device, kwargs):
        if not kwargs['mgmt_ip']:
            return

        return self._is_pingable(**kwargs)
