import requests
from django.shortcuts import render


def home(request):
    state = request.GET.get("state", "").strip().upper()
    city = request.GET.get("city", "").strip()
    first_name = request.GET.get("first_name", "").strip()
    last_name = request.GET.get("last_name", "").strip()
    specialty = request.GET.get("specialty", "").strip()

    providers = []
    error = None

    searched = any([
        state,
        city,
        first_name,
        last_name,
        specialty
    ])

    if searched:
        url = "https://npiregistry.cms.hhs.gov/api/"

        params = {
            "version": "2.1",
            "limit": 20
        }

        if state:
            params["state"] = state

        if city:
            params["city"] = city

        if first_name:
            params["first_name"] = first_name

        if last_name:
            params["last_name"] = last_name

        if specialty:
            params["taxonomy_description"] = specialty

        try:
            response = requests.get(
                url,
                params=params,
                timeout=20
            )

            response.raise_for_status()
            data = response.json()

            if data.get("Errors"):
                error = "; ".join(
                    str(
                        item.get("description")
                        or "Invalid search"
                    )
                    for item in data["Errors"]
                )

            else:
                raw_results = data.get("results") or []

                for provider in raw_results:
                    basic = provider.get("basic") or {}

                    provider_type = provider.get(
                        "enumeration_type", ""
                    )

                    if provider_type == "NPI-1":
                        first = basic.get("first_name") or ""
                        last = basic.get("last_name") or ""

                        name = f"{first} {last}".strip()
                        type_label = "Individual"

                    elif provider_type == "NPI-2":
                        name = (
                            basic.get("organization_name")
                            or ""
                        )
                        type_label = "Organization"

                    else:
                        name = (
                            basic.get("organization_name")
                            or ""
                        )
                        type_label = "Unknown"

                    addresses = provider.get("addresses") or []

                    address = next(
                        (
                            item
                            for item in addresses
                            if item.get("address_purpose")
                            == "LOCATION"
                        ),
                        addresses[0] if addresses else {}
                    )

                    taxonomies = provider.get("taxonomies") or []
                    specialty_list = []
                    seen_specialties = set()

                    for taxonomy in taxonomies:
                        description = (
                            taxonomy.get("desc") or ""
                        ).strip()

                        normalized = description.casefold()

                        if (
                            description
                            and normalized not in seen_specialties
                        ):
                            specialty_list.append(description)
                            seen_specialties.add(normalized)

                    specialty_text = (
                        ", ".join(specialty_list)
                        if specialty_list
                        else "N/A"
                    )

                    street_address = " ".join(
                        str(value).strip()
                        for value in [
                            address.get("address_1"),
                            address.get("address_2")
                        ]
                        if value
                    ) or "N/A"

                    providers.append({
                        "name": name or "N/A",

                        "provider_type": type_label,

                        "npi": (
                            provider.get("number")
                            or "N/A"
                        ),

                        "specialty": specialty_text,

                        "phone": (
                            address.get("telephone_number")
                            or "N/A"
                        ),

                        "address": street_address,

                        "city": (
                            address.get("city")
                            or "N/A"
                        ),

                        "state": (
                            address.get("state")
                            or "N/A"
                        ),

                        "raw_data": provider
                    })

        except requests.RequestException as exc:
            error = (
                "Unable to retrieve provider data: "
                f"{exc}"
            )

        except ValueError:
            error = "The API returned an invalid response."

    context = {
        "providers": providers,
        "result_count": len(providers),
        "state": state,
        "city": city,
        "first_name": first_name,
        "last_name": last_name,
        "specialty": specialty,
        "searched": searched,
        "error": error
    }

    return render(
        request,
        "lookup/home.html",
        context
    )

