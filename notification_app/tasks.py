from django.forms import model_to_dict
from notification_service.celery import app
import requests
from datetime import timedelta, timezone, datetime
from .models import Client, Notification, Message
import json


def _getlist_helper(data):
    res = []
    for qs in data:
        for obj in qs:
            res.append(obj)
    res = set(res)
    return res


@app.task
def send_message(data, client, obj):
    msg = Message.objects.filter(id=obj['id'])[:1].get()
    r = requests.post('https://probe.fbrq.cloud/v1/sent/' + str(obj['id']), data=json.dumps({
        "id": int(obj['id']),
        "phone": int(Client.objects.filter(id=client)[:1].get().phone),
        "text": Notification.objects.filter(id=data['id'])[:1].get().message_text,
    }),
      headers={
          "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODA2MDg1ODYsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6IlN3YWVhbWkifQ.qg14tI8ZTKp41NqNETST9cautCCp6WsKgsizX6v-FAc"
      })
    if r.status_code == 200:
        print("Message delievered successfully (id: " + str(obj['id']) + ")")
        msg.sending_status = "SUCCESS"
        msg.save()
    else:
        end_dt = datetime.fromisoformat(data['end_datetime'][:-1]).astimezone(timezone.utc)
        if end_dt >= datetime.now(tz=timezone.utc)+timedelta(seconds=600):
            send_message.apply_async(args=[data, client, obj], countdown=600)
            msg.sending_status = "IN QUEUE"
            msg.save()
            print("Message not delievered (id: " + str(obj['id']) + "). Next try in 10 minutes")
        else:
            msg.sending_status = "ERROR"
            msg.save()
            print("Message not delievered (id: " + str(obj['id']) + "). Notification is over")


@app.task
def start_notification(data):

    # --------------------- GETTING LIST OG CLIENT IDS FOR NOTIFICATIONS -------------------------------
    # ---------- BY OPERATOR CODE
    data = json.loads(data)
    operator_code_list = data['operator_code_filter']
    clients_by_operator_code__tmp = []  # collecting all querysets as lists of ids...
    for i in operator_code_list:
        clients_by_operator_code__tmp.append(list(Client.objects.values_list('id', flat=True).filter(operator_code=i)))
    clients_op = _getlist_helper(clients_by_operator_code__tmp)
    # ---------- BY TAG
    tag_list = data['tag_filter']
    clients_by_tag__tmp = []
    for i in tag_list:
        clients_by_tag__tmp.append(list(Client.objects.values_list('id', flat=True).filter(tag=i)))
    clients_tag = _getlist_helper(clients_by_operator_code__tmp)

    clients = sorted(list(set(list(clients_tag) + list(clients_op))))

    # ------------ MAKING NEW MESSAGES AND SENDING REQUEST FOR THEM, UPDATING STATUS -------------------
    for client in clients:
        obj = Message.objects.create(sending_datetime=datetime.now(), sending_status="IN QUEUE", notification_id=Notification.objects.filter(id=data['id'])[:1].get(), client=Client.objects.filter(id=client)[:1].get())
        obj.save()
        send_message.apply_async(args=[data, client, model_to_dict(obj)])