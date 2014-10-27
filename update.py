import requests
import ConfigParser
import os


def get_ip():
    response = requests.get('https://icanhazip.com')
    if response.status_code != requests.codes.ok:
        return None
    else:
        return response.text.rstrip('\n')


def update_rackspace(config, ip):
    import pyrax

    def clear_records(domain, fqdn):
        for record in [item for item in dns.get_record_iterator(domain)
                       if item.name == fqdn]:
            dns.delete_record(domain, record)

    domain_list = dict(config.items('domain_records'))
    api_user = config.get('rackspace', 'username')
    api_key = config.get('rackspace', 'apikey')

    pyrax.settings.set('identity_type', 'rackspace')
    pyrax.set_credentials(api_user, api_key)

    dns = pyrax.cloud_dns
    dns.set_timeout(timeout=60)

    for domain in [item for item in dns.get_domain_iterator()
                   if item.name in domain_list]:

        fqdn = '{0}.{1}'.format(domain_list[domain.name], domain.name)
        update_record = {
            'records': [
                {
                    'type': 'A',
                    'name': fqdn,
                    'data': ip,
                    'ttl': 300
                }
            ]
        }

        try:
            record = dns.find_record(domain, record_type='A', name=fqdn)
            update_record['records'][0]['id'] = record.id

            dns.update_records(domain, update_record)

        except (pyrax.exc.DomainRecordNotFound, pyrax.exc.DomainRecordNotUnique):
            # even if we don't find the record originally, we want to delete any potential conflicts
            clear_records(domain, fqdn)
            dns.add_records(domain, update_record['records'])


def main():
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~/.config/updateip.conf'))

    if not config.has_section('config'):
        raise Exception('[config] section missing from configuration file')

    provider = config.get('config', 'provider')
    if not config.has_section(provider):
        raise Exception('[{0}] section missing from configuration file'.format(provider))

    if not config.has_section('domain_records'):
        raise Exception('[domain_records] section missing from configuration file')

    ip = get_ip()
    update_rackspace(config, ip)

if __name__ == '__main__':
    main()
