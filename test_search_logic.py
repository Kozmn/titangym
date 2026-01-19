from logic.nutrition import search_food

def test_search(query):
    print(f"--- Search: {query} ---")
    results = search_food(query, limit=10)
    for res in results:
        print(f"{res['name']} (Cal: {res['calories']})")

if __name__ == "__main__":
    test_search("Rice")
    test_search("Banana")
    test_search("Chicken")
