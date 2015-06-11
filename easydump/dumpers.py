class Dumper(object):
    """
    Class for implementing different ways to dump a database
    """
    @classmethod
    def get_restore_cmd(self, manifest):
        if not self.restore_cmd:
            raise NotImplementedError("Sorry, your database type is not supported yet")
            
        db_name = manifest.database['NAME']
        db_user = manifest.database['USER']
        db_host = manifest.database['HOST']
        db_port = manifest.database['PORT']
        db_pass = manifest.database['PASSWORD']
        
        jobs = manifest.jobs
        
        if hasattr(self, "format_for_restore"):
            vars = self.format_for_restore(**locals())
        else:
            vars = locals()
        
        return self.restore_cmd.format(**vars)

    @classmethod
    def get_dump_cmd(self, manifest):
        if not self.dump_cmd:
            raise NotImplementedError("Sorry, your database type is not supported yet")
        
        db_name = manifest.database['NAME']
        db_user = manifest.database['USER']
        db_host = manifest.database['HOST']
        db_port = manifest.database['PORT']
        db_pass = manifest.database['PASSWORD']
        
        tables = manifest.tables
        
        if hasattr(self, "format_for_dump"):
            vars = self.format_for_dump(**locals())
        else:
            vars = locals()
        
        return self.dump_cmd.format(**vars)

    @classmethod
    def get_drop_cmd(self, manifest):
        if not self.drop_cmd:
            raise NotImplementedError("Sorry, your database type is not supported yet")

        db_name = manifest.database['NAME']
        db_user = manifest.database['USER']
        db_host = manifest.database['HOST']
        db_port = manifest.database['PORT']
        db_pass = manifest.database['PASSWORD']

        tables = manifest.tables

        if hasattr(self, "format_for_drop"):
            vars = self.format_for_drop(**locals())
        else:
            vars = locals()

        return self.drop_cmd.format(**vars)

class PostgresDumper(Dumper):
    drop_cmd = 'psql -U {db_user} {db_user} {db_host} {db_port} {db_pass} -c "DROP DATABASE {db_name};"; ' \
               'psql -U {db_user} {db_user} {db_host} {db_port} {db_pass} -c "CREATE DATABASE {db_name};"'
    restore_cmd = 'pg_restore -U {db_user} {db_host} {db_port} {db_pass} --dbname {db_name} --jobs={jobs} --no-owner easydump'
    dump_cmd = "pg_dump -U {db_user} {db_host} {db_port} {db_pass} --no-acl --clean --oids --no-owner --format=c {tables} {db_name} > easydump"
    
    @classmethod
    def format_for_dump(cls, **kwargs):
        tables = ""
        for table in kwargs['tables']:
            tables = tables + "--table=%s " % table
        kwargs['tables'] = tables
        
        if kwargs['db_pass']:
            kwargs['db_pass'] = ""
        
        if kwargs['db_port']:
            kwargs['db_port'] = "-p %s" % kwargs['db_port']
        
        if kwargs['db_host']:
            kwargs['db_host'] = "-h %s" % kwargs['db_host']
        
        return kwargs

    @classmethod
    def format_for_restore(cls, **kwargs):
        if kwargs['db_pass']:
            kwargs['db_pass'] = "--password"

        if kwargs['db_port']:
            kwargs['db_port'] = "-p %s" % kwargs['db_port']

        if kwargs['db_host']:
            kwargs['db_host'] = "-h %s" % kwargs['db_host']
        
        return kwargs

    @classmethod
    def format_for_drop(cls, **kwargs):
        if kwargs['db_pass']:
            kwargs['db_pass'] = "--password"

        if kwargs['db_port']:
            kwargs['db_port'] = "-p %s" % kwargs['db_port']

        if kwargs['db_host']:
            kwargs['db_host'] = "-h %s" % kwargs['db_host']

        return kwargs

class MySQLDumper(Dumper):
    drop_cmd = None
    restore_cmd = None
    dump_cmd = None

class OracleDumper(Dumper):
    drop_cmd = None
    restore_cmd = None
    dump_cmd = None