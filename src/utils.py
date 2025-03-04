from datetime import datetime   

def generate_timestamp():
        """
        Generates a timestamp string in the format 'yyy-MM-dd-hh-mm-ss'.
        
        Returns:
            str: The formatted timestamp.
        """
        return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")