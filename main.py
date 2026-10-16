
import requests

url = "https://npiregistry.cms.hhs.gov/api/"

state = input("Enter state abbreviation (e.g., NY, CA, TX): ").strip().upper()
city = input("Enter city (e.g., New York, Los Angeles): ").strip()

if not state or not city:
    print("Error: State and city cannot be empty.")
    raise SystemExit(1)

params = {
    "version": "2.1",
    "state": state,
    "city": city,
    "limit": 5
}


response = requests.get(url, params=params, timeout=20)

response.raise_for_status()

data = response.json()


print("Number of results:", data.get("result_count", 0))

for provider in data.get("results", []):

    npi = provider.get("number", "N/A")

    basic = provider.get("basic", {})

    if provider.get("enumeration_type") == "NPI-1":
        first_name = basic.get("first_name", "")
        last_name = basic.get("last_name", "")
        name = f"{first_name} {last_name}".strip()
    else:
        name = basic.get("organization_name", "N/A")

    addresses = provider.get("addresses", [])
    location = next(
        (a for a in addresses if a.get("address_purpose") == "LOCATION"),
        addresses[0] if addresses else {}
    )

    address = location.get("address_1", "N/A")
    city = location.get("city", "N/A")
    state = location.get("state", "N/A")

    taxonomies = provider.get("taxonomies", [])
    primary_taxonomy = next(
        (t for t in taxonomies if t.get("primary")),
        taxonomies[0] if taxonomies else {}
    )
    specialty = primary_taxonomy.get("desc", "N/A")

    print("\n----------------------------")
    print("Provider Name:", name or "N/A")
    print("NPI Number:", npi)
    print("Address:", address)
    print("City:", city)
    print("State:", state)
    print("Specialty:", specialty)

