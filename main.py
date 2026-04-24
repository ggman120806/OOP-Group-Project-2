from models.request import ServiceRequest, ValidationError
from services import CSVreader_service

DATA_FILE = "data/service_requests.csv"
SEARCHABLE_FIELDS = {
    "1": "request_id",
    "2": "request_type",
    "3": "requester_name",
    "4": "location",
    "5": "status",
}


class ServiceRequestManager:
    def __init__(self, file_name: str):
        self.csv_service = CSVreader_service(file_name)
        self.requests = self.csv_service.read_file()

    def display_all_requests(self) -> None:
        if not self.requests:
            print("\nNo requests found.")
            return
        print("\nAll Service Requests")
        print("-" * 70)
        for request in self.requests:
            print(request.summary())

    def add_request(self) -> None:
        print("\nAdd New Service Request")
        print("-" * 30)
        try:
            request = self._collect_request_input()
            if any(existing.request_id.lower() == request.request_id.lower() for existing in self.requests):
                raise ValidationError("A request with that ID already exists.")
            self.requests.append(request)
            self.csv_service.write_file(self.requests)
            print("\nRequest added successfully.")
            print(request.details())
        except ValidationError as exc:
            print(f"\nCould not add request: {exc}")
        except ValueError:
            print("\nCould not add request: numeric input was invalid.")

    def search_requests(self) -> None:
        print("\nSearch Requests By:")
        print("1. Request ID")
        print("2. Request Type")
        print("3. Requester Name")
        print("4. Location")
        print("5. Status")
        choice = input("Select an option: ").strip()
        field_name = SEARCHABLE_FIELDS.get(choice)
        if not field_name:
            print("Invalid search option.")
            return

        value = input("Enter search text: ").strip()
        matches = [request for request in self.requests if request.matches(field_name, value)]

        if not matches:
            print("\nNo matching requests found.")
            return

        print(f"\nFound {len(matches)} matching request(s):")
        print("-" * 70)
        for request in matches:
            print(request.details())
            print("-" * 70)

    def show_analysis(self) -> None:
        if not self.requests:
            print("\nNo requests available for analysis.")
            return

        highest = max(self.requests, key=lambda req: req.priority_score)
        open_requests = [r for r in self.requests if r.status != "Closed"]
        emergency_count = sum(1 for r in self.requests if r.request_type == "Emergency")
        maintenance_count = sum(1 for r in self.requests if r.request_type == "Maintenance")
        event_count = sum(1 for r in self.requests if r.request_type == "EventSupport")
        avg_cost = sum(r.estimated_cost for r in self.requests) / len(self.requests)

        print("\nRequest Analysis")
        print("-" * 40)
        print(f"Total Requests: {len(self.requests)}")
        print(f"Open or In Progress Requests: {len(open_requests)}")
        print(f"Maintenance Requests: {maintenance_count}")
        print(f"Event Support Requests: {event_count}")
        print(f"Emergency Requests: {emergency_count}")
        print(f"Average Estimated Cost: ${avg_cost:.2f}")
        print("\nHighest Priority Request")
        print("-" * 25)
        print(highest.details())

    def _collect_request_input(self) -> ServiceRequest:
        request_id = input("Request ID: ").strip()
        request_type = input("Request Type (Maintenance/EventSupport/Emergency): ").strip()
        requester_name = input("Requester Name: ").strip()
        location = input("Location: ").strip()
        urgency_level = int(input("Urgency Level (1-5): ").strip())
        estimated_cost = float(input("Estimated Cost: ").strip())
        status = input("Status (Open/In Progress/Closed): ").strip()

        issue_type = ""
        days_open = None
        attendees = None
        event_date = ""
        hazard_level = None
        response_time_minutes = None

        if request_type == "Maintenance":
            issue_type = input("Issue Type: ").strip()
            days_open = int(input("Days Open: ").strip())
        elif request_type == "EventSupport":
            attendees = int(input("Expected Attendees: ").strip())
            event_date = input("Event Date (YYYY-MM-DD): ").strip()
        elif request_type == "Emergency":
            hazard_level = int(input("Hazard Level (1-5): ").strip())
            response_time_minutes = int(input("Response Time in Minutes: ").strip())

        return ServiceRequest(
            request_id=request_id,
            request_type=request_type,
            requester_name=requester_name,
            location=location,
            urgency_level=urgency_level,
            estimated_cost=estimated_cost,
            status=status,
            issue_type=issue_type,
            days_open=days_open,
            attendees=attendees,
            event_date=event_date,
            hazard_level=hazard_level,
            response_time_minutes=response_time_minutes,
        )


def main() -> None:
    manager = ServiceRequestManager(DATA_FILE)

    while True:
        print("\nMunicipal Service Request System")
        print("1. Display all requests")
        print("2. Add a new request")
        print("3. Search requests")
        print("4. Analyze requests")
        print("5. Save and exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            manager.display_all_requests()
        elif choice == "2":
            manager.add_request()
        elif choice == "3":
            manager.search_requests()
        elif choice == "4":
            manager.show_analysis()
        elif choice == "5":
            manager.csv_service.write_file(manager.requests)
            print("\nChanges saved. Goodbye.")
            break
        else:
            print("\nInvalid option. Please choose 1-5.")


if __name__ == "__main__":
    main()
