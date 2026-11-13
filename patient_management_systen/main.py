from fastapi import FastAPI,Path,HTTPException
import json
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional
from fastapi.responses import JSONResponse

def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)

    return data

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)

app=FastAPI()


class Patient(BaseModel):
    id:Annotated[str,Field(...,description='ID of the patient',examples=['P001'])]
    name: Annotated[str,Field(...,description='Name of the patient')]
    city: Annotated[str,Field(...,description='City where the patient is living')]
    age: Annotated[int,Field(...,gt=0,lt=120,description='age of the patient')]
    gender:Annotated[Literal['male','female','others'],Field(...,description='Gender of the patient')]
    height:Annotated[float,Field(...,gt=0,description='Height of patient in mtrs')]
    weight:Annotated[float, Field(...,gt=0,description='Weight of patient in kgs')]

    @computed_field
    @property
    def bmi(self)->float:
        return self.weight/(self.height**2)

    @computed_field
    @property
    def verdict(self)->str:
        if(self.bmi<10):
            return 'Underweight'
        elif(self.bmi<25):
            return 'Normal'
        elif(self.bmi<30):
            return 'Normal'
        else:
            return 'Obese'

class UpdatePatient(BaseModel):
    name: Annotated[Optional[str],Field(default=None,description='Name of the patient')]
    city: Annotated[Optional[str],Field(default=None,description='City where the patient is living')]
    age: Annotated[Optional[int],Field(default='My name is Shah',gt=0,lt=120,description='age of the patient')]
    gender:Annotated[Literal['male','female','others'],Field(default=None,description='Gender of the patient')]
    height:Annotated[Optional[float],Field(default='My name is Shah',gt=0,description='Height of patient in mtrs')]
    weight:Annotated[Optional[float], Field(default=None,gt=0,description='Weight of patient in kgs')]


@app.get('/')
def hello():
    return {'message':'Hello World '}


@app.get('/about')
def about():
    return {'message':'My name is Shah'}

@app.get('/view')
def view():
    data=load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id):
    #load all the patients
    data=load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail='patient not found')


@app.get('/sort')
def sort_patients(sort_by:str,order:str):
    valid_fields=['height','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f'Invalid field select from {valid_fields}')

    if order not in ['asc','dsc']:
        raise HTTPException(status_code=400,detail='Invalid order select between asc and dsc')
    
    data=load_data()
    sort_order=True if order=='dsc' else False

    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)

    return sorted_data


@app.post('/create')
def create_patient(patient:Patient):
    #lets check if the patient data is a self validated one or not
    data=load_data()

    #check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400 , detail='Patient already exists')

    #add new patient to our existing database
    data[patient.id]=patient.model_dump(exclude=['id'])

    save_data(data)
    print(data[patient.id])

    return {
        'message':'Data saved Successfully',
        'data':{
            patient.id: data[patient.id]
        }
    }   

@app.put('/edit/{patient_id}')
def update_patient(patient_id:str , patient:UpdatePatient):
    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail="patient not Found")

    existing_patient_info=data[patient_id]

    updated_patient_info=patient.model_dump(exclude_unset=True)

    for key,value in updated_patient_info.items():
        existing_patient_info[key]=value

    #But based on the new values of height and weight , the bmi and verdict will get changed
    #so we will do
    # given dictionery-> pydantic object(so,the bmi and verdict will get updated)
    #  -> dictionery
    existing_patient_info['id']=patient_id
    patient_pydantic_obj=Patient(**existing_patient_info)

    existing_patient_info= patient_pydantic_obj.model_dump(exclude='id')

    data[patient_id]=existing_patient_info

    save_data(data)
    return JSONResponse(status_code=200,content={'message':'patient updated'})


@app.delete('/delete/{patient_id}')
def delete_Patient(patient_id:str):
    #loading the data up
    data=load_data()

    if(patient_id not in data):
        raise HTTPException(status_code=404,detail='Patient not found')

    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200,content={'message':'Patient deleted'})