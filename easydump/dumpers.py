class Dumper(object):
    """
    Class for implementing different ways to dump a database
    """
    @classmethod
    def get_restore_cmd(self, manifest, dump_path):
        if not self.restore_cmd:
            raise NotImplemented("Sorry, your database type is not supported yet")
            
        database_name = manifest.database['NAME']
        database_user = manifest.database['USER']
            
        return restore_cmd.format(**locals())

    @classmethod
    def get_dump_cmd(self, manifest):
        if not self.dump_cmd:
            raise NotImplemented("Sorry, your database type is not supported yet")
        
        database_name = manifest.database['NAME']
        database_user = manifest.database['USER']
        jobs = manifest.jobs
        
        return dump_cmd.format(**locals())

class PostgresDumper(Dumper):
    restore_cmd = 'pg_restore -d {datbase_name} --role={database_user} --jobs={jobs} {dump_path}'
    dump_cmd = "pg_dump --clean --no-owner --format=c {database_name} > dump"
    
class MySQLDumper(Dumper):
    restore_cmd = None
    dump_cmd = None

class OracleDumper(Dumper):
    restore_cmd = None
    dump_cmd = None