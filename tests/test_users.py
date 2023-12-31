# FastAPI
from fastapi import status
# APP
from app.models.user import UserBase, UserFB, UserUpdate
# Test
from .conftest import client, setUp_users 

class TestNewUser:
    def test_create_newuser_blank(self, client: client): 
        response = client.post("/users/newuser")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, "New User whitout fields is not valid" # noqa: E501

    def test_create_newuser_all_fields(self, client: client): 
        userData = {
            "name": "Testing",
            "email": "test@example.com",
            "password": "MyPassword",
            "city": "TestyCity",
            "country": "Testland",
            "userType": "admin"
            }
        response = client.post("/users/newuser",json=userData,)
        userData.pop('password')  # remove password it never should be returned
        userData['userType'] = 'free'       #All created users must be userType 'free'
        assert response.status_code == status.HTTP_201_CREATED, "Status code not 201"
        assert all(key in response.json() for key in userData) , "Response Incomplete or Wrong keys"
        assert UserBase(**response.json()) == UserBase(**userData), "User created is different" 
        assert 'pass_hash' not in response.json() , "pass_hash Should never be in the response"
        #Not necesary, is reduntant
        # assert response.json()['userType'] == 'free', "new users userType always should be free"   
        #Not necesary, is reduntant
        # assert isinstance(response.json(), dict), "Response is not a dictionary"

    def test_create_newuser_repeted(self, client: client):
        user = {
            "name": "Testing",
            "email": "test@example.com",
            "password": "MyPassword"
            }
        client.post("/users/newuser",json=user,)
        response = client.post("/users/newuser",json=user,)
        assert response.status_code == status.HTTP_409_CONFLICT, "Status code not 409 Conflict"

class TestLogin:
    def test_check_login_USER_CRUD(self, client: client, setUp_users: setUp_users):
        user1,user2,user3 = setUp_users
        #Test LogIN
        response = client.post("/userlogin",data= {"username": user1['email'], "password": user1['password']})
        assert response.status_code == status.HTTP_200_OK, "Status code not 200 on login"
        assert 'access_token' in response.json(), "Response must have an access_token"
        assert response.json()['token_type'] == 'bearer', "Response must be token_type 'bearer'"
        header_user1 = {"Authorization" : "Bearer " + response.json()['access_token']}

        #Test Info GET /users/myuser
        response = client.get("/users/myuser", headers=header_user1)
        assert response.status_code == status.HTTP_200_OK, "Status code not 200 on path GET /users/myuser"
        assert all(key in response.json() for key in list(UserFB.__annotations__)) , "Response must have all keys of UserFB"
        assert all(key in response.json() for key in list(UserBase.__annotations__)) , "Response must have all keys of UserFB"
        assert (all( (user1[key] == response.json()[key]) for key in list(UserBase.__annotations__))) , "UserFB returned is different"
        assert 'initDate' in response.json(), "Response must have an initDate"

        #Test Info PUT /users/myuser
        #test User1
        user1_changedata = {"name": "Change User Onw", "email": "testchange@example.com", "password": "otherPassword", "city": "CityChangeOne", "country": "Testland ChangeOne", "userType": "free"}
        response = client.put("/users/myuser", json=UserUpdate(**user1_changedata).dict(),)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Status code not 401_UNAUTHORIZED on path PUT /users/myuser whitout headers"
        response = client.put("/users/myuser", json=user1_changedata , headers=header_user1)
        assert response.status_code == status.HTTP_200_OK, "Status code not 200 on path PUT /users/myuser"
        assert response.json()['email'] == user1['email'], "User email must not change"
        assert response.json()['name'] == user1_changedata['name'], "User name must changed"
        assert response.json()['city'] == user1_changedata['city'], "User city must changed"
        assert response.json()['country'] == user1_changedata['country'], "User country must changed"
        assert response.json()['userType'] == user1['userType'], "User userType must not change"

    def test_check_login_USER_Delete_ChangePassword(self, client: client, setUp_users: setUp_users):
        user1,user2,user3 = setUp_users
        #Test Info DELETE /users/myuser
        response = client.post("/userlogin",data= {"username": user2['email'], "password": user2['password']})
        header_user2 = {"Authorization" : "Bearer " + response.json()['access_token']}
        response = client.delete("/users/myuser",)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Status code not 401_UNAUTHORIZED on path DELETE /users/myuser whitout headers"
        response = client.delete("/users/myuser", headers=header_user2)
        assert response.status_code == status.HTTP_200_OK, "Status code not 200 OK on path DELETE /users/myuser whit headers"
        assert 'disabled' in response.json()['message'], "User must be disabled after deletion"

        #Test Info CHANGE PASSWORD /users/myuser
        new_password_User2 = "newPassword_User2"
        response = client.put("/users/myuser/changepassword",)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Status code not 401_UNAUTHORIZED on path PUT /users/myuser/changepassword whitout headers"
        data_password = {"actual_password": new_password_User2, "new_password": new_password_User2}
        response = client.put("/users/myuser/changepassword", data = data_password ,headers=header_user2)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Status code not 200 OK on path PUT /users/myuser/changepassword whit headers Error Actual password"
        data_password = {"actual_password": user2['password'], "new_password": new_password_User2}
        response = client.put("/users/myuser/changepassword", data = data_password ,headers=header_user2)
        assert response.status_code == status.HTTP_200_OK, "Status code not 200 OK on path PUT /users/myuser/changepassword whit headers Error Actual password"
        response = client.post("/userlogin",data= {"username": user2['email'], "password": user2['password']})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Status code not 401_UNAUTHORIZED on path LOGIN whit old password"
        response = client.post("/userlogin",data= {"username": user2['email'], "password": new_password_User2})
        assert response.status_code == status.HTTP_200_OK, "Status code not 200 OK on path on  LOGIN whit new password"
    
