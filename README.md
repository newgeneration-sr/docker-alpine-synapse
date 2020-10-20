# Synapse Matrix on Alpine Linux + S6 Overlay

# Auto configuration parameters :

- POSTGRES_PASSWORD=password (the password of the db container)

- SYNAPSE_ROOT_USER=root (auto create root user on the server)
- SYNAPSE_ROOT_PASSWORD=root

(basic configuration flags of the homeserver synapse)
- SYNAPSE_NO_TLS=true 
- SYNAPSE_ENABLE_REGISTRATION=true
- SYNAPSE_GENERATE=true
- SYNAPSE_CONFIG_DIR=/data
- SYNAPSE_CONFIG_PATH=/data/homeserver.yaml
- SYNAPSE_SERVER_NAME=matrix.test.example
- SYNAPSE_REPORT_STATS=yes
- SYNAPSE_TURN_URIS=stun.l.google.com:19302,stun1.l.google.om:19302,stun2.l.google.com:19302,stun3.l.google.com:19302,stun4.l.google.com:19302
    

# TODO features :
- auto backups

# Compose file exemple

```
version: '3.1'

services:

  synapse:
    build: .
    restart: unless-stopped
    environment:
      - POSTGRES_PASSWORD=synapse
      - POSTGRES_DB=synapse
      - POSTGRES_HOST=db

      - SYNAPSE_ROOT_USER=root
      - SYNAPSE_ROOT_PASSWORD=root

      - SYNAPSE_NO_TLS=true 
      - SYNAPSE_ENABLE_REGISTRATION=true
      - SYNAPSE_CONFIG_DIR=/data
      - SYNAPSE_CONFIG_PATH=/data/homeserver.yaml
      - SYNAPSE_SERVER_NAME=matrix.test.example
      - SYNAPSE_REPORT_STATS=yes
    ports:
      - 8448:8448/tcp
      - 8009:8009
      - 8008:8008
    depends_on:
      - db

  db:
    image: dotriver/postgres
    environment:
      - PGDATA=/var/lib/postgresql/data
      - PSQL_USER=root
      - PSQL_PASS=root
      - PSQL_INITDB_ARGS=-E 'UTF8' --lc-collate='C' --lc-ctype='C'
      - PGSQL_ROOT_ACCESS="all"
      
      - DB_0_NAME=synapse
      - DB_0_PASS=synapse
    volumes:
      - dbdata:/var/lib/postgresql/data
    ports:
      - 5432:5432

  omnidb:
    image: dotriver/omnidb
    environment:
      - OMNIDB_USER=root
      - OMNIDB_PASS=root

      - DB_TECH=postgresql
      - DB_HOST=localhost
      - DB_PORT=5432
      - DB_USER=root
      - DB_NAME=synapse
    ports:
      - 8080:8080
      - 25482:25482
    depends_on:
      - db

volumes:
    dbdata:
```
