import pandas as pd
import re

class RuleBasedStockEngine:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self._load_and_clean()

    def _normalize_concentration(self, val):
        if pd.isna(val):
            return "Unspecified"
        val = str(val).strip()
        val = re.sub(r'\s+', ' ', val)
        val = re.sub(r'(\d+)\s*M', r'\1 M', val, flags=re.IGNORECASE)
        val = re.sub(r'(\d+)\s*%', r'\1%', val)
        return val

    def _load_and_clean(self):
        self.raw_stock = pd.read_excel(self.excel_path, sheet_name='Stock_Data')
        self.min_stock = pd.read_excel(self.excel_path, sheet_name='Minimum_Stock')

        location_map = {
            'HYD': 'Hyderabad',
            'HYDERBAD': 'Hyderabad',
            'HYD.': 'Hyderabad',
            'HYDERABAD': 'Hyderabad',
            'BENGALURU': 'Bangalore',
            'BANGALORE': 'Bangalore',
            'BANGLORE': 'Bangalore',
            'BLR': 'Bangalore'
        }

        df = self.raw_stock.copy()
        df['Loc_Clean'] = df['Location'].astype(str).str.strip().str.upper().map(location_map).fillna('UNKNOWN')
        df['Conc_Clean'] = df['Concentration'].apply(self._normalize_concentration)
        df['CAS_Clean'] = df['CAS_Number'].astype(str).str.strip()
        df['Product_Clean'] = df['Product_Name'].astype(str).str.strip()

        self.min_stock['CAS_Clean'] = self.min_stock['CAS_Number'].astype(str).str.strip()
        self.min_stock['Conc_Clean'] = self.min_stock['Concentration'].apply(self._normalize_concentration)

        self.anomalies = df[(df['Quantity'] <= 0) | (df['Loc_Clean'] == 'UNKNOWN')].copy()
        self.valid_stock = df[(df['Quantity'] > 0) & (df['Loc_Clean'] != 'UNKNOWN')].copy()

        self.agg_stock = self.valid_stock.groupby(
            ['CAS_Clean', 'Product_Clean', 'Conc_Clean', 'Loc_Clean', 'Unit'], as_index=False
        )['Quantity'].sum()

    def get_stock_by_cas(self, cas_number: str, location: str = None):
        res = self.agg_stock[self.agg_stock['CAS_Clean'].str.lower() == cas_number.strip().lower()]
        if location and location.lower() != 'all':
            res = res[res['Loc_Clean'].str.lower() == location.strip().lower()]
        return res

    def get_concentrations(self, cas_number: str):
        res = self.agg_stock[self.agg_stock['CAS_Clean'].str.lower() == cas_number.strip().lower()]
        return res[['CAS_Clean', 'Product_Clean', 'Conc_Clean']].drop_duplicates()

    def check_low_stock(self, threshold: int = 5):
        tot = self.valid_stock.groupby(['CAS_Clean', 'Product_Clean', 'Conc_Clean', 'Unit'], as_index=False)['Quantity'].sum()
        tot['Threshold'] = threshold
        tot['Deficit'] = threshold - tot['Quantity']
        low = tot[tot['Quantity'] < threshold].copy()
        return low

    def get_location_exclusive(self, loc_a: str = "Hyderabad", loc_b: str = "Bangalore"):
        a_cas = set(self.agg_stock[self.agg_stock['Loc_Clean'] == loc_a]['CAS_Clean'])
        b_cas = set(self.agg_stock[self.agg_stock['Loc_Clean'] == loc_b]['CAS_Clean'])
        exclusive_cas = a_cas - b_cas
        return self.agg_stock[(self.agg_stock['Loc_Clean'] == loc_a) & (self.agg_stock['CAS_Clean'].isin(exclusive_cas))]

    def parse_and_query(self, user_query: str):
        query_lower = user_query.lower().strip()

        location = None
        if any(loc in query_lower for loc in ['hyderabad', 'hyd']):
            location = 'Hyderabad'
        elif any(loc in query_lower for loc in ['bangalore', 'bengaluru', 'blr']):
            location = 'Bangalore'

        cas_match = re.search(r'\b\d{2,7}-\d{2}-\d\b', user_query)
        cas_number = cas_match.group(0) if cas_match else None

        matched_product = None
        known_products = self.agg_stock['Product_Clean'].unique()
        for p in sorted(known_products, key=len, reverse=True):
            if p.lower() in query_lower:
                matched_product = p
                break

        matched_conc = None
        known_concs = self.agg_stock['Conc_Clean'].unique()
        for c in sorted(known_concs, key=len, reverse=True):
            c_tokens = [t.lower() for t in re.split(r'\s+', c) if t.lower() not in ['in']]
            if all(tok in query_lower for tok in c_tokens):
                matched_conc = c
                break

        if any(w in query_lower for w in ['concentration', 'concentrations', 'molarity']):
            if cas_number:
                res = self.get_concentrations(cas_number)
                explanation = f"Extracted Intent: GET_CONCENTRATIONS | CAS: {cas_number}"
                return res, explanation
            elif matched_product:
                res = self.agg_stock[self.agg_stock['Product_Clean'] == matched_product][['CAS_Clean', 'Product_Clean', 'Conc_Clean']].drop_duplicates()
                explanation = f"Extracted Intent: GET_CONCENTRATIONS | Product: {matched_product}"
                return res, explanation
            else:
                return "Please specify a product or CAS number to check concentrations.", "Intent: GET_CONCENTRATIONS (Missing Entity)"

        elif any(w in query_lower for w in ['minimum', 'below', 'low stock', 'reorder', 'shortage', 'alert']):
            res = self.check_low_stock(threshold=5)
            explanation = "Extracted Intent: CHECK_LOW_STOCK | Threshold: Stock < 5"
            return res, explanation

        elif 'exclusive' in query_lower or ('hyderabad' in query_lower and 'not' in query_lower and 'bangalore' in query_lower):
            res = self.get_location_exclusive("Hyderabad", "Bangalore")
            explanation = "Extracted Intent: EXCLUSIVE_STOCK | Compare: Hyderabad vs Bangalore"
            return res, explanation

        else:
            res = self.agg_stock.copy()
            filters = []
            if cas_number:
                res = res[res['CAS_Clean'].str.lower() == cas_number.lower()]
                filters.append(f"CAS: {cas_number}")
            if matched_product:
                res = res[res['Product_Clean'] == matched_product]
                filters.append(f"Product: {matched_product}")
            if matched_conc:
                res = res[res['Conc_Clean'] == matched_conc]
                filters.append(f"Concentration: {matched_conc}")
            if location:
                res = res[res['Loc_Clean'].str.lower() == location.lower()]
                filters.append(f"Location: {location}")

            if not filters:
                filters.append("Showing total aggregated inventory")

            explanation = f"Extracted Intent: STOCK_LOOKUP | Filter: {' & '.join(filters)}"
            return res, explanation