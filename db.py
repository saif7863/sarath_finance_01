"""
Mr. Goli Soda Finance - Database Module
FINAL VERSION - DIRECT SUPABASE CALLS
"""

from supabase import create_client, Client

SUPABASE_URL = "https://pvsmqmcchewpunlqjnpl.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2c21xbWNjaGV3cHVubHFqbnBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxMTY2NDksImV4cCI6MjA5NzY5MjY0OX0.T1VH8BHEjze8Op2wElrDaOwQhTrpyXqHNVGXG98r67Y"

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
print("✅ Database connected")


class SimpleCursor:
    def __init__(self, commit=False):
        self.result = []
        self.query_type = None
    
    def execute(self, query, params=None):
        """Execute query - route directly without SQL parsing"""
        try:
            q = query.upper().strip()
            
            # SETTINGS
            if "SELECT" in q and "SETTINGS" in q:
                print("→ GET settings")
                r = supabase.table("settings").select("*").eq("id", 1).execute()
                self.result = r.data or [{"id": 1, "fee": 0, "budget_limit": 0, "warning": 0}]
            
            elif "UPDATE" in q and "SETTINGS" in q:
                print("→ UPDATE settings")
                r = supabase.table("settings").update({"fee": params[0], "budget_limit": params[1], "warning": params[2]}).eq("id", 1).execute()
                self.result = r.data or []
            
            # FRANCHISES
            elif "SELECT" in q and "FRANCHISES" in q:
                print("→ GET franchises")
                r = supabase.table("franchises").select("*").order("id").execute()
                self.result = r.data or []
                print(f"   Found {len(self.result)} franchises")
            
            elif "INSERT" in q and "FRANCHISES" in q:
                print(f"→ INSERT franchise: {params}")
                r = supabase.table("franchises").insert({"name": params[0], "state": params[1]}).execute()
                self.result = r.data or [{"name": params[0], "state": params[1]}]
            
            elif "UPDATE" in q and "FRANCHISES" in q:
                print(f"→ UPDATE franchise")
                r = supabase.table("franchises").update({"name": params[0], "state": params[1]}).eq("id", params[2]).execute()
                self.result = r.data or []
            
            elif "DELETE" in q and "FRANCHISES" in q:
                print(f"→ DELETE franchise {params[0]}")
                supabase.table("franchises").delete().eq("id", params[0]).execute()
                self.result = []
            
            # CATEGORIES
            elif "SELECT" in q and "CATEGOR" in q:
                print("→ GET categories")
                r = supabase.table("categories").select("*").order("id").execute()
                self.result = r.data or []
                print(f"   Found {len(self.result)} categories")
            
            elif "INSERT" in q and "CATEGOR" in q:
                print(f"→ INSERT category: {params}")
                r = supabase.table("categories").insert({"name": params[0]}).execute()
                self.result = r.data or [{"name": params[0]}]
            
            elif "UPDATE" in q and "CATEGOR" in q:
                print(f"→ UPDATE category")
                r = supabase.table("categories").update({"name": params[0]}).eq("id", params[1]).execute()
                self.result = r.data or []
            
            elif "DELETE" in q and "CATEGOR" in q:
                print(f"→ DELETE category {params[0]}")
                supabase.table("categories").delete().eq("id", params[0]).execute()
                self.result = []
            
            # ENTRIES
            elif "SELECT" in q and "ENTRIES" in q:
                print("→ GET entries")
                r = supabase.table("entries_with_details").select("*").order("date", desc=True).execute()
                self.result = r.data or []
                print(f"   Found {len(self.result)} entries")
            
            elif "INSERT" in q and "ENTRIES" in q:
                print(f"→ INSERT entry")
                r = supabase.table("entries").insert({
                    "edate": params[0],
                    "franchise_id": params[1],
                    "category_id": params[2],
                    "descr": params[3],
                    "amount": float(params[4]),
                    "invoice": params[5],
                    "bill": params[6],
                    "remarks": params[7]
                }).execute()
                self.result = r.data or []
            
            elif "UPDATE" in q and "ENTRIES" in q:
                print(f"→ UPDATE entry")
                r = supabase.table("entries").update({
                    "edate": params[0],
                    "franchise_id": params[1],
                    "category_id": params[2],
                    "descr": params[3],
                    "amount": float(params[4]),
                    "invoice": params[5],
                    "bill": params[6],
                    "remarks": params[7]
                }).eq("id", params[8]).execute()
                self.result = r.data or []
            
            elif "DELETE" in q and "ENTRIES" in q:
                print(f"→ DELETE entry {params[0]}")
                supabase.table("entries").delete().eq("id", params[0]).execute()
                self.result = []
            
            else:
                print(f"⚠️  Unhandled: {query[:40]}")
                self.result = []
        
        except Exception as e:
            print(f"❌ Error: {e}")
            self.result = []
    
    def fetchone(self):
        if not self.result:
            return None
        return self.result[0] if self.result else None
    
    def fetchall(self):
        return self.result
    
    def executemany(self, query, params_list):
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
    return CursorContext(commit)


def init_db():
    print("✅ Database ready")
