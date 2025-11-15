from django.shortcuts import render
from django.http import JsonResponse
import random
import time
from agora_token_builder import RtcTokenBuilder
from .models import RoomMember
import json
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json



# Create your views here.

def lobby(request):
    return render(request, 'base/lobby.html')

def room(request):
    return render(request, 'base/room.html')

def getToken(request):
    appId = settings.AGORA_APP_ID
    appCertificate = settings.AGORA_APP_CERTIFICATE
    channelName = request.GET.get('channel')
    uid = random.randint(1, 230)
    expirationTimeInSeconds = 3600
    currentTimeStamp = int(time.time())
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(
        appId, appCertificate, channelName, uid, role, privilegeExpiredTs
    )

    return JsonResponse({'token': token, 'uid': uid}, safe=False)

@csrf_exempt
def createMember(request):
    data = json.loads(request.body)
    member, created = RoomMember.objects.get_or_create(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name']
    )

    return JsonResponse({'name':data['name']}, safe=False)


def getMember(request):
    uid = request.GET.get('UID')
    room_name = request.GET.get('room_name')

    member = RoomMember.objects.get(
        uid=uid,
        room_name=room_name,
    )
    name = member.name
    return JsonResponse({'name':member.name}, safe=False)

@csrf_exempt
def deleteMember(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data['name']
        room_name = data['room_name']
        
        try:
            member = RoomMember.objects.get(
                name=name,
                room_name=room_name
            )
            member.delete()
            return JsonResponse({'message': 'Member deleted successfully'}, safe=False)
        except RoomMember.DoesNotExist:
            # Member doesn't exist, but that's okay - maybe already deleted
            return JsonResponse({'message': 'Member not found, but no action needed'}, safe=False)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def room(request):
    return render(request, 'base/room.html', {
        'app_id': settings.AGORA_APP_ID
    })