import uuid
from queue_service import send_message
from random_report_generator import generate_random_bill

def receive_message():
    return {
        "id": uuid.uuid4(),
        "data":generate_random_bill()
    }

def main():
    for _ in range(10):
        message = receive_message()
        print("Sending Message")
        print(message)
        send_message(message)
        print()
        
if __name__ == "__main__":
    main()