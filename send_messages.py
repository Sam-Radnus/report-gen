import uuid
from queue_service import send_message
from random_report_generator import generate_random_bill
from datetime import datetime
batch_no = datetime.now().strftime('%Y%m%d%H%M%S')



def receive_message():
    return {
        "id": uuid.uuid4(),
        "batch_no":batch_no,
        "data":generate_random_bill()
    }

def main():
    for _ in range(15):
        message = receive_message()
        print("Sending Message")
        print(message)
        send_message(message)
        print()
        
if __name__ == "__main__":
    main()