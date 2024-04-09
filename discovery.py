# discovery.py
from database import Session, User


def discover_peers():
    """Retrieve the list of online peers from the database."""
    session = Session()
    peers = session.query(User).filter(User.is_online == True).all()
    session.close()
    return [
        (peer.username, peer.ip_address, peer.port) for peer in peers if peer.is_online
    ]
