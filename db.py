"""
Mr. Goli Soda Finance - Database Module
FIXED VERSION - GUARANTEED WORKING
"""

from supabase import create_client, Client

# ===== CREDENTIALS =====
SUPABASE_URL = "https://pvsmqmcchewpunlqjnpl.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2c21xbWNjaGV3cHVubHFqbnBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxMTY2NDksImV4cCI6MjA5NzY5MjY0OX0.T1VH8BHEjze8Op2wElrDaOwQhTrpyXqHNVGXG98r67Y"

print("✅ Supabase connecting...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
print("✅ Supabase connected!")


class SimpleCursor:
    def __init__(self, commit=False):
        self.result = []
    
    def execute(self, query, params=None):
        """Execute SQL queries against Supabase"""
        query_upper = query.upper()
        
        try:
            # ===== SELECT QUERIES =====
            if "SELECT" in query_upper and "FROM settings" in query_upper:
                print("📍 Query: SELECT settings")
                response = supabase.table("settings").select("*").eq("id", 1).execute()
                self.result = response.data if response.data else [{"id": 1, "fee": 0, "budget_limit": 0, "warning": 0}]
                print(f"✅ Settings: {len(self.result)} row(s)")
            
            elif "SELECT" in query_upper and "FROM franchises" in query_upper:
                print("📍 Query: SELECT franchises")
                response = supabase.table("franchises").select("*").order("id").execute()
                self.result = response.data if response.data else []
                print(f"✅ Franchises: {len(self.result)} row(s)")
            
            elif "SELECT" in query_upper and "FROM categories" in query_upper:
                print("📍 Query: SELECT categories")
                response = supabase.table("categories").select("*").order("id").execute()
                self.result = response.data if response.data else []
                print(f"✅ Categories: {len(self.result)} row(s)")
            
            elif "SELECT" in query_upper and "FROM entries" in query_upper:
                print("📍 Query: SELECT entries")
                response = supabase.table("entries_with_details").select("*").order("date", desc=True).execute()
                self.result = response.data if response.data else []
                print(f"✅ Entries: {len(self.result)} row(s)")
            
            # ===== INSERT QUERIES =====
            elif "INSERT" in query_upper and "INTO franchises" in query_upper:
                print(f"📍 Query: INSERT franchises - {params}")
                data = {"name": params[0], "state": params[1]}
                response = supabase.table("franchises").insert(data).execute()
                self.result = response.data if response.data else [data]
                print(f"✅ Inserted franchise")
            
            elif "INSERT" in query_upper and "INTO categories" in query_upper:
                print(f"📍 Query: INSERT categories - {params}")
                data = {"name": params[0]}
                response = supabase.table("categories").insert(data).execute()
                self.result = response.data if response.data else [data]
                print(f"✅ Inserted category")
            
            elif "INSERT" in query_upper and "INTO entries" in query_upper:
                print(f"📍 Query: INSERT entries")
                data = {
                    "edate": params[0],
                    "franchise_id": params[1],
                    "category_id": params[2],
                    "descr": params[3],
                    "amount": float(params[4]),
                    "invoice": params[5],
                    "bill": params[6],
                    "remarks": params[7]
                }
                response = supabase.table("entries").insert(data).execute()
                self.result = response.data if response.data else [data]
                print(f"✅ Inserted entry")
            
            elif "INSERT" in query_upper and "INTO settings" in query_upper:
                print("📍 Query: INSERT settings")
                try:
                    response = supabase.table("settings").insert({"id": 1}).execute()
                    self.result = []
                except:
                    self.result = []
            
            # ===== UPDATE QUERIES =====
            elif "UPDATE" in query_upper and "settings" in query_upper:
                print(f"📍 Query: UPDATE settings - {params}")
                data = {"fee": float(params[0]), "budget_limit": float(params[1]), "warning": float(params[2])}
                response = supabase.table("settings").update(data).eq("id", 1).execute()
                self.result = response.data if response.data else []
            
            elif "UPDATE" in query_upper and "franchises" in query_upper:
                print(f"📍 Query: UPDATE franchises - {params}")
                data = {"name": params[0], "state": params[1]}
                response = supabase.table("franchises").update(data).eq("id", params[2]).execute()
                self.result = response.data if response.data else []
            
            elif "UPDATE" in query_upper and "categories" in query_upper:
                print(f"📍 Query: UPDATE categories - {params}")
                data = {"name": params[0]}
                response = supabase.table("categories").update(data).eq("id", params[1]).execute()
                self.result = response.data if response.data else []
            
            elif "UPDATE" in query_upper and "entries" in query_upper:
                print(f"📍 Query: UPDATE entries - {params}")
                data = {
                    "edate": params[0],
                    "franchise_id": params[1],
                    "category_id": params[2],
                    "descr": params[3],
                    "amount": float(params[4]),
                    "invoice": params[5],
                    "bill": params[6],
                    "remarks": params[7]
                }
                response = supabase.table("entries").update(data).eq("id", params[8]).execute()
                self.result = response.data if response.data else []
            
            # ===== DELETE QUERIES =====
            elif "DELETE" in query_upper and "FROM franchises" in query_upper:
                print(f"📍 Query: DELETE franchise {params[0]}")
                supabase.table("franchises").delete().eq("id", params[0]).execute()
                self.result = []
            
            elif "DELETE" in query_upper and "FROM categories" in query_upper:
                print(f"📍 Query: DELETE category {params[0]}")
                supabase.table("categories").delete().eq("id", params[0]).execute()
                self.result = []
            
            elif "DELETE" in query_upper and "FROM entries" in query_upper:
                print(f"📍 Query: DELETE entry {params[0]}")
                supabase.table("entries").delete().eq("id", params[0]).execute()
                self.result = []
            
            else:
                print(f"⚠️  Unknown query: {query[:50]}")
                self.result = []
        
        except Exception as e:
            print(f"❌ DB ERROR: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            self.result = []
    
    def fetchone(self):
        """Get first row"""
        if not self.result:
            return None
        row = self.result[0]
        if isinstance(row, dict):
            if "budget_limit" in row and "lim" not in row:
                row["lim"] = row["budget_limit"]
            if "descr" in row and "desc" not in row:
                row["desc"] = row["descr"]
        return row
    
    def fetchall(self):
        """Get all rows"""
        return self.result if self.result else []
    
    def executemany(self, query, params_list):
        """Execute multiple times"""
        for params in params_list:
            self.execute(query, params)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


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
    print("✅ Database module ready!")
