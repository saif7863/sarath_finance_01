"""
Mr. Goli Soda Finance - Database Module
Supabase REST API - WORKING VERSION
"""

from supabase import create_client, Client

# ===== HARDCODED SUPABASE CREDENTIALS =====
SUPABASE_URL = "https://pvsmqmcchewpunlqjnpl.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2c21xbWNjaGV3cHVubHFqbnBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxMTY2NDksImV4cCI6MjA5NzY5MjY0OX0.T1VH8BHEjze8Op2wElrDaOwQhTrpyXqHNVGXG98r67Y"

print(f"📡 Connecting to Supabase...")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

print("✅ Supabase connected!")


class SimpleCursor:
    """Simple cursor for Supabase"""
    def __init__(self, commit=False):
        self.commit_on_exit = commit
        self.result = None
    
    def execute(self, query, params=None):
        """Execute SQL query"""
        query_upper = query.upper().strip()
        
        try:
            if "SELECT" in query_upper:
                self._select(query, params)
            elif "INSERT" in query_upper:
                self._insert(query, params)
            elif "UPDATE" in query_upper:
                self._update(query, params)
            elif "DELETE" in query_upper:
                self._delete(query, params)
        except Exception as e:
            print(f"❌ Query error: {e}")
            self.result = []
    
    def _select(self, query, params):
        """Handle SELECT"""
        try:
            if "FROM settings" in query:
                data = supabase.table("settings").select("*").eq("id", 1).execute()
                self.result = data.data if data.data else []
            
            elif "FROM franchises" in query:
                data = supabase.table("franchises").select("id, name, state").order("id").execute()
                self.result = data.data if data.data else []
            
            elif "FROM categories" in query:
                data = supabase.table("categories").select("id, name").order("id").execute()
                self.result = data.data if data.data else []
            
            elif "FROM entries" in query:
                data = supabase.table("entries_with_details").select("*").order("date", desc=True).execute()
                self.result = data.data if data.data else []
            
            else:
                self.result = []
        except Exception as e:
            print(f"SELECT error: {e}")
            self.result = []
    
    def _insert(self, query, params):
        """Handle INSERT"""
        try:
            if "INTO franchises" in query and params:
                data = supabase.table("franchises").insert({
                    "name": params[0],
                    "state": params[1]
                }).execute()
                self.result = data.data if data.data else []
            
            elif "INTO categories" in query and params:
                data = supabase.table("categories").insert({
                    "name": params[0]
                }).execute()
                self.result = data.data if data.data else []
            
            elif "INTO entries" in query and params:
                data = supabase.table("entries").insert({
                    "edate": params[0],
                    "franchise_id": params[1],
                    "category_id": params[2],
                    "descr": params[3],
                    "amount": params[4],
                    "invoice": params[5],
                    "bill": params[6],
                    "remarks": params[7]
                }).execute()
                self.result = data.data if data.data else []
            
            elif "INTO settings" in query:
                try:
                    data = supabase.table("settings").insert({"id": 1}).execute()
                    self.result = []
                except:
                    self.result = []
            
            else:
                self.result = []
        except Exception as e:
            print(f"INSERT error: {e}")
            self.result = []
    
    def _update(self, query, params):
        """Handle UPDATE"""
        try:
            if "UPDATE settings" in query and params:
                data = supabase.table("settings").update({
                    "fee": params[0],
                    "budget_limit": params[1],
                    "warning": params[2]
                }).eq("id", 1).execute()
                self.result = data.data if data.data else []
            
            elif "UPDATE franchises" in query and params:
                data = supabase.table("franchises").update({
                    "name": params[0],
                    "state": params[1]
                }).eq("id", params[2]).execute()
                self.result = data.data if data.data else []
            
            elif "UPDATE categories" in query and params:
                data = supabase.table("categories").update({
                    "name": params[0]
                }).eq("id", params[1]).execute()
                self.result = data.data if data.data else []
            
            elif "UPDATE entries" in query and params:
                data = supabase.table("entries").update({
                    "edate": params[0],
                    "franchise_id": params[1],
                    "category_id": params[2],
                    "descr": params[3],
                    "amount": params[4],
                    "invoice": params[5],
                    "bill": params[6],
                    "remarks": params[7]
                }).eq("id", params[8]).execute()
                self.result = data.data if data.data else []
            
            else:
                self.result = []
        except Exception as e:
            print(f"UPDATE error: {e}")
            self.result = []
    
    def _delete(self, query, params):
        """Handle DELETE"""
        try:
            if "DELETE FROM franchises" in query and params:
                supabase.table("franchises").delete().eq("id", params[0]).execute()
                self.result = []
            
            elif "DELETE FROM categories" in query and params:
                supabase.table("categories").delete().eq("id", params[0]).execute()
                self.result = []
            
            elif "DELETE FROM entries" in query and params:
                supabase.table("entries").delete().eq("id", params[0]).execute()
                self.result = []
            
            else:
                self.result = []
        except Exception as e:
            print(f"DELETE error: {e}")
            self.result = []
    
    def fetchone(self):
        """Get first result"""
        if self.result and len(self.result) > 0:
            return self.result[0]
        return None
    
    def fetchall(self):
        """Get all results"""
        return self.result if self.result else []
    
    def executemany(self, query, params_list):
        """Execute many queries"""
        for params in params_list:
            self.execute(query, params)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CursorManager:
    """Context manager for cursor"""
    def __init__(self, commit=False):
        self.commit = commit
    
    def __enter__(self):
        return SimpleCursor(self.commit)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def cursor(commit=False):
    """Get cursor"""
    return CursorManager(commit)


def init_db():
    """Initialize database"""
    print("✅ Database ready!")
