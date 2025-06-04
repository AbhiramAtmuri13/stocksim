import pika
import json

def publish_order(order_data: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="order_queue")
    channel.basic_publish(
        exchange="",
        routing_key="order_queue",
        body=json.dumps(order_data)
    )
    connection.close()
