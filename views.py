import requests
from django.shortcuts import render


def home(request):
    providers = []
    result_count = None
    error = None

    state = request.GET.get("state", "").strip().upper()
    city = request.GET.get("city", "").strip()

    if state and city:
        url = "https://npiregistry.cms.hhs.gov/api/"

        params = {
            "version": "2.1",
            "state": state,
            "city": city,
            "limit": 5
        }

        try:
            response = requests.get(
                url, params=params, timeout=20
            )
            response.raise_for_status()
            data = response.json()

            for provider in data.get("results", []):
                npi = provider.get("number", "N/A")
                basic = provider.get("basic", {})

                if provider.get("enumeration_type") == "NPI-1":
                    first_name = basic.get("first_name", "")
                    last_name = basic.get("last_name", "")
                    name = f"{first_name} {last_name}".strip()
                else:
                    name = basic.get(
                        "organization_name", "N/A"
                    )

                addresses = provider.get("addresses", [])

                location = next(
                    (
                        a for a in addresses
                        if a.get("address_purpose") == "LOCATION"
                    ),
                    addresses[0] if addresses else {}
                )

                address = location.get("address_1", "N/A")
                provider_city = location.get("city", "N/A")
                provider_state = location.get("state", "N/A")

                taxonomies = provider.get("taxonomies", [])

                primary = next(
                    (
                        t for t in taxonomies
                        if t.get("primary")
                    ),
                    taxonomies[0] if taxonomies else {}
                )

                specialty = primary.get("desc", "N/A")

                providers.append({
                    "name": name,
                    "npi": npi,
                    "specialty": specialty,
                    "address": address,
                    "city": provider_city,
                    "state": provider_state
                })

            result_count = len(providers)

        except requests.RequestException as e:
            error = f"Unable to retrieve provider data: {e}"

    elif state or city:
        error = "Please enter both state and city."

    return render(request, "lookup/home.html", {
        "providers": providers,
        "result_count": result_count,
        "state": state,
        "city": city,
        "error": error
    })
