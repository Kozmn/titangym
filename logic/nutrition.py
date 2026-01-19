import requests

def search_food(query, limit=10):
    """
    Searches OpenFoodFacts for the given query.
    Returns a list of dicts with 'name', 'calories', 'protein', 'carbs', 'fat' (per 100g).
    Sorts results to prefer simple, exact matches over complex branded items.
    """
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    # Fetch more results initially to allow for filtering and re-ranking
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 100, 
        "sort_by": "unique_scans_n"
    }
    
    candidates = []
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        products = data.get('products', [])
        
        for product in products:
            nutriments = product.get('nutriments', {})
            product_name = product.get('product_name', '')
            
            if not product_name or not product_name.strip():
                continue
                
            # Normalize name for scoring
            name_lower = product_name.lower().strip()
            query_lower = query.lower().strip()
            
            # Basic validation: must have some nutrition info
            calories = nutriments.get('energy-kcal_100g')
            if calories is None:
                kj = nutriments.get('energy_100g')
                if kj:
                    calories = kj / 4.184
                else:
                    calories = 0
            
            # Skip items with zero calories AND zero protein (likely bad data or water/additives)
            # unless query is explicitly for something like "water"
            if calories == 0 and nutriments.get('proteins_100g', 0) == 0 and "water" not in query_lower:
                continue

            item = {
                "name": product_name,
                "calories": float(calories),
                "protein": float(nutriments.get('proteins_100g', 0)),
                "carbs": float(nutriments.get('carbohydrates_100g', 0)),
                "fat": float(nutriments.get('fat_100g', 0))
            }

            # Scoring Logic
            # Lower score is better (like rank)
            score = 0
            
            # 1. Exact match (Overwhelming bonus)
            if name_lower == query_lower:
                score -= 1000
            
            # 2. Starts with query (bonus)
            elif name_lower.startswith(query_lower):
                score -= 50
                
            # 3. Contains query (prerequisite usually, but good to check)
            if query_lower in name_lower:
                score -= 10
            
            # 4. Penalty for length
            # Add 2 points per character over the query length to penalize long names heavily
            length_penalty = (len(name_lower) - len(query_lower)) * 2
            score += length_penalty
            
            candidates.append((score, item))
            
        # Sort by score
        candidates.sort(key=lambda x: x[0])
        
        # Return top N items
        return [c[1] for c in candidates[:limit]]
        
    except Exception as e:
        print(f"Error fetching food data: {e}")
        return []
