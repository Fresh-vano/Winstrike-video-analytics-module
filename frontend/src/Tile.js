import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Paper } from '@material-ui/core';

const useStyles = makeStyles(() => ({
  tile: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '20px',
    borderRadius: '10px',
  },
}));

const Tile = ({ children }) => {
  const classes = useStyles();

  return <Paper className={classes.tile}>{children}</Paper>;
};

export default Tile;