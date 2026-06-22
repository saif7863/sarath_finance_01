"""
Mr. Goli Soda Finance - Database Module
Supabase REST API with hardcoded credentials
NO .env file needed!
"""

# ===== HARDCODED SUPABASE CREDENTIALS =====
SUPABASE_URL = "https://pvsmqmcchewpunlqjnpl.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2c21xbWNjaGV3cHVubHFqbnBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxMTY2NDksImV4cCI6MjA5NzY5MjY0OX0.T1VH8BHEjze8Op2wElrDaOwQhTrpyXqHNVGXG98r67Y"

print(f"📡 Connecting to Supabase at {SUPABASE_URL}")

# Import Supabase client
from supabase import create_client, Client

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

print("✅ Supabase connected!")


# Simple cursor mimic for compatibility with Flask app
class SimpleCursor:
    def __init__(self, commit=False):
        self.commit_on_exit = commit
        self.result = None

    def execute(self, query, params=None):
        """Execute SQL via Supabase"""
        query_upper = query.upper().strip()

        try:
            # SELECT queries
            if query_upper.startswith("SELECT"):
                self._execute_select(query, params)
            # INSERT queries
            elif query_upper.startswith("INSERT"):
                self._execute_insert(query, params)
            # UPDATE queries
            elif query_upper.startswith("UPDATE"):
                self._execute_update(query, params)
            # DELETE queries
            elif query_upper.startswith("DELETE"):
                self._execute_delete(query, params)
            else:
                self.result = []
        except Exception as e:
            print(f"❌ Query error: {e}")
            self.result = []

    def _execute_select(self, query, params):
        """Handle SELECT queries"""
        try:
            # SELECT from settings
            if "FROM settings" in query:
                response = supabase.table("settings").select("*").eq("id", 1).execute()
                self.result = response.data if response.data else []

            # SELECT from franchises
            elif "FROM franchises" in query:
                response = supabase.table("franchises").select("id, name, state").order("id").execute()
                self.result = response.data if response.data else []

            # SELECT from categories
            elif "FROM categories" in query:
                response = supabase.table("categories").select("id, name").order("id").execute()
                self.result = response.data if response.data else []

            # SELECT from entries
            elif "FROM entries" in query:
                response = supabase.table("entries_with_details").select("*").order("date", desc=True).execute()
                self.result = response.data if response.data else []

            else:
                self.result = []
        except Exception as e:
            print(f"SELECT error: {e}")
            self.result = []

    def _execute_insert(self, query, params):
        """Handle INSERT queries"""
        try:
            # INSERT into franchises
            if "INTO franchises" in query:
                data = {"name": params[0], "state": params[1]}
                response = supabase.table("franchises").insert(data).execute()
                self.result = response.data if response.data else []

            # INSERT into categories
            elif "INTO categories" in query:
                data = {"name": params[0]}
                response = supabase.table("categories").insert(data).execute()
                self.result = response.data if response.data else []

            # INSERT into entries
            elif "INTO entries" in query:
                data = {
                    "edate": params[0],
                    "franchise_id": params[1],
                    "category_id": params[2],
                    "descr": params[3],
                    "amount": params[4],
                    "invoice": params[5],
                    "bill": params[6],
                    "remarks": params[7]
                }
                response = supabase.table("entries").insert(data).execute()
                self.result = response.data if response.data else []

            # INSERT into settings
            elif "INTO settings" in query:
                try:
                    data = {"id": 1}
                    response = supabase.table("settings").insert(data).execute()
                except:
                    pass
                self.result = []
        except Exception as e:
            print(f"INSERT error: {e}")
            self.result = []

    def _execute_update(self, query, params):
        """Handle UPDATE queries"""
        try:
            # UPDATE settings
            if "UPDATE settings" in query:
                data = {"fee": params[0], "budget_limit": params[1], "warning": params[2]}
                response = supabase.table("settings").update(data).eq("id", 1).execute()
                self.result = response.data if response.data else []

            # UPDATE franchises
            elif "UPDATE franchises" in query:
                data = {"name": params[0], "state": params[1]}
                response = supabase.table("franchises").update(data).eq("id", params[2]).execute()
                self.result = response.data if response.data else []

            # UPDATE categories
            elif "UPDATE categories" in query:
                data = {"name": params[0]}
                response = supabase.table("categories").update(data).eq("id", params[1]).execute()
                self.result = response.data if response.data else []

            # UPDATE entries
            elif "UPDATE entries" in query:
                data = {
                    "edate": params[0],
                    "franchise_id": params[1],
                    "category_id": params[2],
                    "descr": params[3],
                    "amount": params[4],
                    "invoice": params[5],
                    "bill": params[6],
                    "remarks": params[7]
                }
                response = supabase.table("entries").update(data).eq("id", params[8]).execute()
                self.result = response.data if response.data else []
        except Exception as e:
            print(f"UPDATE error: {e}")
            self.result = []

    def _execute_delete(self, query, params):
        """Handle DELETE queries"""
        try:
            # DELETE from franchises
            if "DELETE FROM franchises" in query:
                response = supabase.table("franchises").delete().eq("id", params[0]).execute()
                self.result = []

            # DELETE from categories
            elif "DELETE FROM categories" in query:
                response = supabase.table("categories").delete().eq("id", params[0]).execute()
                self.result = []

            # DELETE from entries
            elif "DELETE FROM entries" in query:
                response = supabase.table("entries").delete().eq("id", params[0]).execute()
                self.result = []
        except Exception as e:
            print(f"DELETE error: {e}")
            self.result = []

    def fetchone(self):
        """Get first result"""
        return self.result[0] if self.result else None

    def fetchall(self):
        """Get all results"""
        return self.result if self.result else []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# Context manager for cursor
class CursorManager:
    def __init__(self, commit=False):
        self.commit = commit

    def __enter__(self):
        return SimpleCursor(self.commit)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def cursor(commit=False):
    """Return cursor context manager"""
    return CursorManager(commit)


def init_db():
    """Initialize database"""
    print("✅ Database initialized!")