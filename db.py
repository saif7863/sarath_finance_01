"""
Mr. Goli Soda Finance - Database Module
ULTRA SIMPLE - Direct Supabase calls
"""

from supabase import create_client, Client

# ===== CREDENTIALS =====
SUPABASE_URL = "https://pvsmqmcchewpunlqjnpl.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2c21xbWNjaGV3cHVubHFqbnBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxMTY2NDksImV4cCI6MjA5NzY5MjY0OX0.T1VH8BHEjze8Op2wElrDaOwQhTrpyXqHNVGXG98r67Y"

# Create client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

print("✅ Database connected!")


# ===== SIMPLE CURSOR CLASS =====
class SimpleCursor:
    def __init__(self, commit=False):
        self.result = []
    
    def execute(self, query, params=None):
        """Simple SQL execution"""
        query = query.upper()
        
        try:
            # SELECT FROM SETTINGS
            if "SELECT" in query and "FROM settings" in query:
                response = supabase.table("settings").select("*").eq("id", 1).execute()
                self.result = response.data
            
            # SELECT FROM FRANCHISES
            elif "SELECT" in query and "FROM franchises" in query:
                response = supabase.table("franchises").select("id, name, state").order("id", desc=False).execute()
                self.result = response.data
            
            # SELECT FROM CATEGORIES
            elif "SELECT" in query and "FROM categories" in query:
                response = supabase.table("categories").select("id, name").order("id", desc=False).execute()
                self.result = response.data
            
            # SELECT FROM ENTRIES
            elif "SELECT" in query and "FROM entries" in query:
                response = supabase.table("entries_with_details").select("*").order("date", desc=True).execute()
                self.result = response.data
            
            # INSERT INTO FRANCHISES
            elif "INSERT" in query and "INTO franchises" in query:
                if params:
                    response = supabase.table("franchises").insert({
                        "name": params[0],
                        "state": params[1]
                    }).execute()
                    self.result = response.data
            
            # INSERT INTO CATEGORIES
            elif "INSERT" in query and "INTO categories" in query:
                if params:
                    response = supabase.table("categories").insert({
                        "name": params[0]
                    }).execute()
                    self.result = response.data
            
            # INSERT INTO ENTRIES
            elif "INSERT" in query and "INTO entries" in query:
                if params:
                    response = supabase.table("entries").insert({
                        "edate": params[0],
                        "franchise_id": params[1],
                        "category_id": params[2],
                        "descr": params[3],
                        "amount": float(params[4]),
                        "invoice": params[5],
                        "bill": params[6],
                        "remarks": params[7]
                    }).execute()
                    self.result = response.data
            
            # INSERT INTO SETTINGS
            elif "INSERT" in query and "INTO settings" in query:
                try:
                    response = supabase.table("settings").insert({"id": 1}).execute()
                except:
                    pass
                self.result = []
            
            # UPDATE SETTINGS
            elif "UPDATE" in query and "settings" in query:
                if params:
                    response = supabase.table("settings").update({
                        "fee": float(params[0]),
                        "budget_limit": float(params[1]),
                        "warning": float(params[2])
                    }).eq("id", 1).execute()
                    self.result = response.data
            
            # UPDATE FRANCHISES
            elif "UPDATE" in query and "franchises" in query:
                if params:
                    response = supabase.table("franchises").update({
                        "name": params[0],
                        "state": params[1]
                    }).eq("id", params[2]).execute()
                    self.result = response.data
            
            # UPDATE CATEGORIES
            elif "UPDATE" in query and "categories" in query:
                if params:
                    response = supabase.table("categories").update({
                        "name": params[0]
                    }).eq("id", params[1]).execute()
                    self.result = response.data
            
            # UPDATE ENTRIES
            elif "UPDATE" in query and "entries" in query:
                if params:
                    response = supabase.table("entries").update({
                        "edate": params[0],
                        "franchise_id": params[1],
                        "category_id": params[2],
                        "descr": params[3],
                        "amount": float(params[4]),
                        "invoice": params[5],
                        "bill": params[6],
                        "remarks": params[7]
                    }).eq("id", params[8]).execute()
                    self.result = response.data
            
            # DELETE FROM FRANCHISES
            elif "DELETE" in query and "FROM franchises" in query:
                if params:
                    response = supabase.table("franchises").delete().eq("id", params[0]).execute()
                self.result = []
            
            # DELETE FROM CATEGORIES
            elif "DELETE" in query and "FROM categories" in query:
                if params:
                    response = supabase.table("categories").delete().eq("id", params[0]).execute()
                self.result = []
            
            # DELETE FROM ENTRIES
            elif "DELETE" in query and "FROM entries" in query:
                if params:
                    response = supabase.table("entries").delete().eq("id", params[0]).execute()
                self.result = []
            
            else:
                self.result = []
        
        except Exception as e:
            print(f"Error: {e}")
            self.result = []
    
    def fetchone(self):
        """Get first row"""
        if self.result:
            row = self.result[0]
            # Convert column names: budget_limit -> lim, descr -> desc
            if isinstance(row, dict):
                if "budget_limit" in row:
                    row["lim"] = row["budget_limit"]
                if "descr" in row:
                    row["desc"] = row["descr"]
            return row
        return None
    
    def fetchall(self):
        """Get all rows"""
        return self.result
    
    def executemany(self, query, params_list):
        """Execute multiple times"""
        for params in params_list:
            self.execute(query, params)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# Cursor context manager
class CursorContext:
    def __init__(self, commit=False):
        self.commit = commit
    
    def __enter__(self):
        return SimpleCursor(self.commit)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def cursor(commit=False):
    """Get cursor"""
    return CursorContext(commit)


def init_db():
    """Initialize DB"""
    print("✅ Database ready!")
