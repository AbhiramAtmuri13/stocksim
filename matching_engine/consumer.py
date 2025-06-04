import pika
import json

def process_order(order):
    print(f"[MATCHING ENGINE] Received order: {order}")
    # Matching logic will go here in next sprint

def consume_orders():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="order_queue")

    def callback(ch, method, properties, body):
        order = json.loads(body)
        process_order(order)

    channel.basic_consume(
        queue="order_queue", on_message_callback=callback, auto_ack=True
    )

    print("[MATCHING ENGINE] Waiting for orders...")
    channel.start_consuming()

if __name__ == "__main__":
    consume_orders()
