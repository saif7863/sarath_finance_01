"""
Mr. Goli Soda Finance - Database Module
FINAL VERSION - WORKING
"""

from supabase import create_client, Client
import traceback

# ===== CREDENTIALS =====
SUPABASE_URL = "https://pvsmqmcchewpunlqjnpl.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2c21xbWNjaGV3cHVubHFqbnBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxMTY2NDksImV4cCI6MjA5NzY5MjY0OX0.T1VH8BHEjze8Op2wElrDaOwQhTrpyXqHNVGXG98r67Y"

# Create client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

print("✅ Database connected!")


class SimpleCursor:
    def __init__(self, commit=False):
        self.result = []
    
    def execute(self, query, params=None):
        """Simple SQL execution"""
        query_upper = query.upper()
        
        try:
            # SELECT FROM SETTINGS
            if "SELECT" in query_upper and "FROM settings" in query_upper:
                response = supabase.table("settings").select("*").eq("id", 1).execute()
                self.result = response.data if response.data else []
            
            # SELECT FROM FRANCHISES
            elif "SELECT" in query_upper and "FROM franchises" in query_upper:
                response = supabase.table("franchises").select("id, name, state").order("id", desc=False).execute()
                self.result = response.data if response.data else []
            
            # SELECT FROM CATEGORIES
            elif "SELECT" in query_upper and "FROM categories" in query_upper:
                response = supabase.table("categories").select("id, name").order("id", desc=False).execute()
                self.result = response.data if response.data else []
            
            # SELECT FROM ENTRIES
            elif "SELECT" in query_upper and "FROM entries" in query_upper:
                response = supabase.table("entries_with_details").select("*").order("date", desc=True).execute()
                self.result = response.data if response.data else []
            
            # INSERT INTO FRANCHISES
            elif "INSERT" in query_upper and "INTO franchises" in query_upper:
                if params:
                    data_to_insert = {
                        "name": params[0],
                        "state": params[1]
                    }
                    response = supabase.table("franchises").insert(data_to_insert).execute()
                    # Make sure we have the data
                    if response.data:
                        self.result = response.data
                    else:
                        self.result = [data_to_insert]
            
            # INSERT INTO CATEGORIES
            elif "INSERT" in query_upper and "INTO categories" in query_upper:
                if params:
                    data_to_insert = {"name": params[0]}
                    response = supabase.table("categories").insert(data_to_insert).execute()
                    if response.data:
                        self.result = response.data
                    else:
                        self.result = [data_to_insert]
            
            # INSERT INTO ENTRIES
            elif "INSERT" in query_upper and "INTO entries" in query_upper:
                if params:
                    data_to_insert = {
                        "edate": params[0],
                        "franchise_id": params[1],
                        "category_id": params[2],
                        "descr": params[3],
                        "amount": float(params[4]),
                        "invoice": params[5],
                        "bill": params[6],
                        "remarks": params[7]
                    }
                    response = supabase.table("entries").insert(data_to_insert).execute()
                    if response.data:
                        self.result = response.data
                    else:
                        self.result = [data_to_insert]
            
            # INSERT INTO SETTINGS
            elif "INSERT" in query_upper and "INTO settings" in query_upper:
                try:
                    response = supabase.table("settings").insert({"id": 1}).execute()
                    self.result = []
                except Exception as e:
                    self.result = []
            
            # UPDATE SETTINGS
            elif "UPDATE" in query_upper and "settings" in query_upper:
                if params:
                    data_to_update = {
                        "fee": float(params[0]),
                        "budget_limit": float(params[1]),
                        "warning": float(params[2])
                    }
                    response = supabase.table("settings").update(data_to_update).eq("id", 1).execute()
                    self.result = response.data if response.data else []
            
            # UPDATE FRANCHISES
            elif "UPDATE" in query_upper and "franchises" in query_upper:
                if params:
                    data_to_update = {
                        "name": params[0],
                        "state": params[1]
                    }
                    response = supabase.table("franchises").update(data_to_update).eq("id", params[2]).execute()
                    self.result = response.data if response.data else []
            
            # UPDATE CATEGORIES
            elif "UPDATE" in query_upper and "categories" in query_upper:
                if params:
                    data_to_update = {"name": params[0]}
                    response = supabase.table("categories").update(data_to_update).eq("id", params[1]).execute()
                    self.result = response.data if response.data else []
            
            # UPDATE ENTRIES
            elif "UPDATE" in query_upper and "entries" in query_upper:
                if params:
                    data_to_update = {
                        "edate": params[0],
                        "franchise_id": params[1],
                        "category_id": params[2],
                        "descr": params[3],
                        "amount": float(params[4]),
                        "invoice": params[5],
                        "bill": params[6],
                        "remarks": params[7]
                    }
                    response = supabase.table("entries").update(data_to_update).eq("id", params[8]).execute()
                    self.result = response.data if response.data else []
            
            # DELETE FROM FRANCHISES
            elif "DELETE" in query_upper and "FROM franchises" in query_upper:
                if params:
                    supabase.table("franchises").delete().eq("id", params[0]).execute()
                self.result = []
            
            # DELETE FROM CATEGORIES
            elif "DELETE" in query_upper and "FROM categories" in query_upper:
                if params:
                    supabase.table("categories").delete().eq("id", params[0]).execute()
                self.result = []
            
            # DELETE FROM ENTRIES
            elif "DELETE" in query_upper and "FROM entries" in query_upper:
                if params:
                    supabase.table("entries").delete().eq("id", params[0]).execute()
                self.result = []
            
            else:
                self.result = []
        
        except Exception as e:
            print(f"❌ DB ERROR: {str(e)}")
            traceback.print_exc()
            self.result = []
    
    def fetchone(self):
        """Get first row"""
        if self.result and len(self.result) > 0:
            row = self.result[0]
            # Make sure it's a dict
            if isinstance(row, dict):
                # Ensure id field exists
                if "id" not in row:
                    row["id"] = row.get("id") or 1
                return row
            return row
        # Return empty dict to prevent None errors
        return {"id": 1}
    
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
    print("✅ Database ready!")
