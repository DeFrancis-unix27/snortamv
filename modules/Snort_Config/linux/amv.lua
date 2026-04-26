---------------------------------------------------------------------------
-- 1. configure defaults
---------------------------------------------------------------------------

-- Network variables
HOME_NET = 'any'
EXTERNAL_NET = 'any'

-- Rule path
RULE_PATH = './rules/generated'

include 'snort_defaults.lua'

---------------------------------------------------------------------------
-- 2. configure inspection
---------------------------------------------------------------------------

stream = { }
stream_ip = { }
stream_icmp = { }
stream_tcp = { }
stream_udp = { }
stream_user = { }
stream_file = { }

arp_spoof = { }
back_orifice = { }
dns = { }
imap = { }
netflow = {}
normalizer = { }
pop = { }
rpc_decode = { }
sip = { }
socks = { }
ssh = { }
ssl = { }
telnet = { }

cip = { }
dnp3 = { }
iec104 = { }
mms = { }
modbus = { }
opcua = { }
s7commplus = { }

dce_smb = { }
dce_tcp = { }
dce_udp = { }
dce_http_proxy = { }
dce_http_server = { }

gtp_inspect = default_gtp
port_scan = default_med_port_scan
smtp = default_smtp

ftp_server = default_ftp_server
ftp_client = { }
ftp_data = { }

http_inspect = { }
http2_inspect = { }

file_inspect = { rules_file = 'file_magic.rules' }
file_policy = { }

js_norm = default_js_norm

appid = { }

---------------------------------------------------------------------------
-- 3. configure bindings
---------------------------------------------------------------------------

wizard = default_wizard

binder =
{
    { when = { proto = 'udp', ports = '53', role='server' },  use = { type = 'dns' } },
    { when = { proto = 'tcp', ports = '53', role='server' },  use = { type = 'dns' } },

    { use = { type = 'wizard' } }
}

---------------------------------------------------------------------------
-- 5. configure detection  (FIXED SECTION)
---------------------------------------------------------------------------

references = default_references
classifications = default_classifications

ips =
{
    enable_builtin_rules = true,

    -- ✅ Use your generated rules
    rules = [[
        include ]] .. RULE_PATH .. [[/snort.rules
    ]],

    variables = default_variables
}

---------------------------------------------------------------------------
-- 8. configure tweaks
---------------------------------------------------------------------------

if ( tweaks ~= nil ) then
    include(tweaks .. '.lua')
end
