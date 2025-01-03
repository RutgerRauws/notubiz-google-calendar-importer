from attrs import define
import cattrs
import yaml

@define 
class Config:
    organisation_id: int
    weeks_ahead: int
    google_mail_address: str
    google_calendar_id: str

    @staticmethod
    def read_config(file_name: str = "./config.yaml") -> 'Config':
        data : any
        
        with open(file_name, 'r') as file:
            data = yaml.safe_load(file)

        config = cattrs.structure(data, Config)

        return config