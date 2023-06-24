import React, { useState } from 'react';
import { Table, TableHead, TableBody, TableRow, TableCell, Typography, makeStyles, TableContainer, Paper } from '@material-ui/core';

const useStyles = makeStyles(() => ({
  tableContainer: {
    maxHeight: 400,
    minHeight: 400,
  },
  table: {
    overflowY: 'auto',
  },
  tableRow: {
    maxHeight: '100px',
  },
}));

const EventTable = ({data, videoRef}) => {
  const [hoveredRow, setHoveredRow] = useState(null);

  const jumpToTime = (time) => {
    if (videoRef.current) {
      debugger
      const [hour, minutes, seconds] = time.split(':').map(Number);
      const totalSeconds = hour * 60 * 60 + minutes * 60 + seconds;
      videoRef.current.currentTime = totalSeconds;
    }
  };

  const compareTime = (a, b) => {
    const timeA = new Date(`1970-01-01T${a.time}`);
    const timeB = new Date(`1970-01-01T${b.time}`);
    return timeA - timeB;
  };

  const sortedData = [...data].sort(compareTime);

  const handleRowHover = (index) => {
    setHoveredRow(index);
  };

  const classes = useStyles();

  return (
    <>
      <Typography variant="h5" align="center">Произошедшие события</Typography>
      <TableContainer component={Paper} className={classes.tableContainer}>
        <Table className={classes.table}>
          <TableHead>
            <TableRow>
              <TableCell>ID события</TableCell>
              <TableCell>Класс техники</TableCell>
              <TableCell>Событие</TableCell>
              <TableCell>Начало события</TableCell>
              <TableCell>Конец события</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedData.map((event, index) => (
              <TableRow key={event.event_id} className={classes.tableRow} onMouseEnter={() => handleRowHover(index)} onMouseLeave={() => handleRowHover(null)} style={{ backgroundColor: index === hoveredRow ? 'lightgray' : 'white' }}>
                <TableCell>{event.event_id}</TableCell>
                <TableCell>{event.transport_name}</TableCell>
                <TableCell>{event.event}</TableCell>
                <TableCell style={{ cursor:'pointer' }} onClick={() => {jumpToTime(event.time)}}>{event.time}</TableCell>
                <TableCell style={{ cursor:'pointer' }} onClick={() => {jumpToTime(event.time_end)}}>{event.time_end}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
};

export default EventTable;