from bisect import bisect_left
import datetime
from typing import Union, Tuple, Optional, NewType, List

# Common types
FrameID = int
ObjectID = str
DateTime = datetime.datetime
Coordinate2D = Tuple[float, float]
Speed2D = Tuple[float, float]

# Helper Functions
def str2timestamp(s: str) -> DateTime:
    """Converts string into timeframe
    Args:
        s (str): timestamp string
    Returns:
        datetime.datetime:
    """

    if len(s) > 19:
        # for the case if seconds are not rounded to integers
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")
    # for the case if seconds ARE rounded to integers
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")


class Detection:
    def __init__(
        self,
        id: ObjectID,
        detection_class: str,
        frame: FrameID,
        timestamp: Union[str, DateTime],
        x: float,
        y: float,
    ) -> None:
        self.id = id
        self.detection_class = detection_class
        self.frames = [frame]

        self.timestamps = [
            str2timestamp(timestamp) if str == type(timestamp) else timestamp
        ]
        self.X = [x]
        self.Y = [y]
        self.Vx = [0]
        self.Vy = [0]

    def __calculate_speed(self, X: List[float], T: List[DateTime]) -> float:
        """Internal function used to add speed to list when we add new frame with add_frame function

        Args:
            X (List[float]): [description]
            T (List[DateTime]): [description]

        Returns:
            float: dX / dT
        """
        dx = X[-1] - X[-2]
        dt = (T[-1] - T[-2]).total_seconds()
        return dx / dt

    def add_frame(self, frame: FrameID, ts: Union[str, DateTime], x: float, y: float):
        """Add New frame to the detection
            For the object id we append the new frame with the new coordinates and timestamp
        Args:
            frame (int): frame_id from the metadata
            ts (Union[str, datetime.datetime]): timestamp from the metadata
            x (float): x-coordinate
            y (float): y-coordinate
        """
        self.frames.append(frame)
        if str == type(ts):
            ts = str2timestamp(ts)
        self.timestamps.append(ts)
        self.X.append(x)
        self.Y.append(y)
        if len(self.X) > 1:
            self.Vx.append(self.__calculate_speed(self.X, self.timestamps))
            self.Vy.append(self.__calculate_speed(self.Y, self.timestamps))

    def get_coord(self, frame_id: FrameID) -> Coordinate2D:
        """Find coordinates of the object by frame_id

        Args:
            frame_id (int): [description]

        Returns:
            Tuple[float, float]: coordinates where the object would be in dt seconds
        """
        # better through exception than process
        ind = bisect_left(self.frames, frame_id)
        return self.X[ind], self.Y[ind]

    def get_timestamp(self, frame_id: FrameID) -> DateTime:
        """Find timestamp of the object by frame_id

        Args:
            frame_id (int): [description]

        Returns:
            DateTime: timestamp
        """
        # better through exception than process
        ind = bisect_left(self.frames, frame_id)
        return self.timestamps[ind]


    def get_speed(self, frame_id: int) -> Speed2D:
        """Find Speed Vector of the object by frame_id

        Args:
            frame_id (int): [description]

        Returns:
            Tuple[float, float]: (Vx,Vy) for the current postion x,y
        """

        # better through exception than process
        ind = bisect_left(self.frames, frame_id)
        return self.Vx[ind], self.Vy[ind]

    def get_coord_projection(
        self, frame_id: FrameID, dt: Optional[float] = 0
    ) -> Coordinate2D:
        """Find predicted location of object from frame = frame_id into dt seconds

        Args:
            frame_id (int): [description]
            dt (Optional[float], optional): Seconds to see object projection Defaults to 0.

        Returns:
            Tuple[float, float]: [description]
        """
        # return projected coordinates withing t seconds assuming that speed would not change
        # X = x0 + Vx * t
        # Y = y0 + Vy * t
        x0, y0 = self.get_coord(frame_id)
        Vx, Vy = self.get_speed(frame_id)

        return x0 + Vx * dt, y0 + Vy * dt

    def get_future_location(self, dt: Optional[float] = 0) -> Coordinate2D:
        """Prediction of future location within after some time dt (seconds)

        Args:
            dt (int, optional): [description]. Defaults to 1.

        Returns:
            [type]: (x,y) coordinates where the object would be in dt seconds
        """
        return self.get_coord_projection(frame_id=self.frames[-1], dt=dt)
