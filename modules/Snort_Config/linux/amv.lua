-- =========================
-- 1. Defaults
-- =========================

HOME_NET = 'any'
EXTERNAL_NET = 'any'

RULE_PATH = '/root/snortamv/rules/generated'

include 'snort_defaults.lua'

-- =========================
-- 2. Inspection
-- =========================

stream = default_stream
stream_tcp = default_stream_tcp
stream_udp = default_stream_udp
stream_icmp = default_stream_icmp

http_inspect = default_http_inspect
ftp_server = default_ftp_server
smtp = default_smtp
dns = { }

ssh = { }
ssl = { }

-- =========================
-- 3. Bindings
-- =========================

wizard = default_wizard

binder =
{
    { when = { proto = 'udp', ports = '53', role='server' }, use = { type = 'dns' } },
    { when = { proto = 'tcp', ports = '53', role='server' }, use = { type = 'dns' } },

    { use = { type = 'wizard' } }
}

-- =========================
-- 4. Detection
-- =========================

ips =
{
    enable_builtin_rules = false,

    rules = [[
        include ]] .. RULE_PATH .. [[/snort.rules
    ]],

    variables = default_variables
}