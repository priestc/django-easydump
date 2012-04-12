class Dumper(object):
    """
    Class for implementing different ways to dump a database
    """
    @classmethod
    def get_restore_cmd(self, manifest):
        if not self.restore_cmd:
            raise NotImplemented("Sorry, your database type is not supported yet")
            
        database_name = manifest.database['NAME']
        database_user = manifest.database['USER']
        jobs = manifest.jobs
        
        if hasattr(self, "format_for_restore"):
            vars = self.format_for_restore(**locals())
        else:
            vars = locals()
        
        return self.restore_cmd.format(**vars)

    @classmethod
    def get_dump_cmd(self, manifest):
        if not self.dump_cmd:
            raise NotImplemented("Sorry, your database type is not supported yet")
        
        database_name = manifest.database['NAME']
        database_user = manifest.database['USER']
        tables = manifest.tables
        
        if hasattr(self, "format_for_dump"):
            vars = self.format_for_dump(**locals())
        else:
            vars = locals()
        
        return self.dump_cmd.format(**vars)

class PostgresDumper(Dumper):
    restore_cmd = 'pg_restore --dbname {database_name} --role={database_user} --jobs={jobs} easydump'
    dump_cmd = "pg_dump --clean --no-owner --format=c {tables} {database_name} > easydump"
    
    @classmethod
    def format_for_dump(cls, **kwargs):
        tables = ""
        for table in kwargs['tables']:
            tables = tables + "--table %s " % table
        
        kwargs.update({'tables': tables})
        return kwargs
    
class MySQLDumper(Dumper):
    restore_cmd = None
    dump_cmd = None

class OracleDumper(Dumper):
    restore_cmd = None
    dump_cmd = None