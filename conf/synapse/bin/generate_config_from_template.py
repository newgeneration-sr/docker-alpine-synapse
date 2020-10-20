#!/synapse/bin/python3

import os
import subprocess
import sys
import codecs
import glob

import jinja2

def log(txt):
    print(txt, file=sys.stderr)

def convert(src, dst, environ):
    """Generate a file from a template
    Args:
        src (str): path to input file
        dst (str): path to file to write
        environ (dict): environment dictionary, for replacement mappings.
    """
    with open(src) as infile:
        template = infile.read()
    rendered = jinja2.Template(template).render(**environ)
    with open(dst, "w") as outfile:
        outfile.write(rendered)

def generate_config_from_template(config_dir, config_path, environ, ownership):
    """Generate a homeserver.yaml from environment variables
    Args:
        config_dir (str): where to put generated config files
        config_path (str): where to put the main config file
        environ (dict): environment dictionary
        ownership (str|None): "<user>:<group>" string which will be used to set
            ownership of the generated configs. If None, ownership will not change.
    """
    for v in ("SYNAPSE_SERVER_NAME", "SYNAPSE_REPORT_STATS"):
        if v not in environ:
            error(
                "Environment variable '%s' is mandatory when generating a config file."
                % (v,)
            )

    # populate some params from data files (if they exist, else create new ones)
    environ = environ.copy()
    secrets = {
        "registration": "SYNAPSE_REGISTRATION_SHARED_SECRET",
        "macaroon": "SYNAPSE_MACAROON_SECRET_KEY",
    }

    for name, secret in secrets.items():
        if secret not in environ:
            filename = "/data/%s.%s.key" % (environ["SYNAPSE_SERVER_NAME"], name)

            # if the file already exists, load in the existing value; otherwise,
            # generate a new secret and write it to a file

            if os.path.exists(filename):
                log("Reading %s from %s" % (secret, filename))
                with open(filename) as handle:
                    value = handle.read()
            else:
                log("Generating a random secret for {}".format(secret))
                value = codecs.encode(os.urandom(32), "hex").decode()
                with open(filename, "w") as handle:
                    handle.write(value)
            environ[secret] = value

    environ["SYNAPSE_APPSERVICES"] = glob.glob("/data/appservices/*.yaml")
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)

    # Convert SYNAPSE_NO_TLS to boolean if exists
    if "SYNAPSE_NO_TLS" in environ:
        tlsanswerstring = str.lower(environ["SYNAPSE_NO_TLS"])
        if tlsanswerstring in ("true", "on", "1", "yes"):
            environ["SYNAPSE_NO_TLS"] = True
        else:
            if tlsanswerstring in ("false", "off", "0", "no"):
                environ["SYNAPSE_NO_TLS"] = False
            else:
                error(
                    'Environment variable "SYNAPSE_NO_TLS" found but value "'
                    + tlsanswerstring
                    + '" unrecognized; exiting.'
                )

    if "SYNAPSE_LOG_CONFIG" not in environ:
        environ["SYNAPSE_LOG_CONFIG"] = config_dir + "/log.config"

    log("Generating synapse config file " + config_path)
    convert("/homeserver.yaml", config_path, environ)

    log_config_file = environ["SYNAPSE_LOG_CONFIG"]
    log("Generating log config file " + log_config_file)
    convert("/log.config", log_config_file, environ)

    # Hopefully we already have a signing key, but generate one if not.
    args = [
        "/synapse/bin/python3",
        "-B",
        "-m",
        "synapse.app.homeserver",
        "--config-path",
        config_path,
        # tell synapse to put generated keys in /data rather than /compiled
        "--keys-directory",
        config_dir,
        "--generate-keys",
    ]

    if ownership is not None:
        subprocess.check_output(["chown", "-R", ownership, "/data"])
        args = ["gosu", ownership] + args

    subprocess.check_output(args)


environ = os.environ
desired_uid = int(environ.get("UID", "991"))
desired_gid = int(environ.get("GID", "991"))
config_dir = environ.get("SYNAPSE_CONFIG_DIR", "/data")
config_path = environ.get("SYNAPSE_CONFIG_PATH", config_dir + "/homeserver.yaml")
if (desired_uid == os.getuid()) and (desired_gid == os.getgid()):
    ownership = None
else:
    ownership = "{}:{}".format(desired_uid, desired_gid)

#print( config_dir, config_path, environ, ownership )
generate_config_from_template(config_dir, config_path, environ, ownership)