import React from 'react'
import { Line } from 'react-chartjs-2'
import {Chart as ChartJS, CategoryScale, registerables} from 'chart.js'
import { Typography } from '@material-ui/core';

ChartJS.register(CategoryScale);
ChartJS.register(...registerables);

const LineChart = ({data}) => {

  return (
    <>
      <Typography variant="h5" align="center">Простой техники</Typography>
      <div>
        <Line
          data={{
              labels: ['00:00', '01:00','02:00','03:00','04:00','05:00'],
              datasets: data
          }}
          height={400}
          width={600}
          options={{
            responsive: true,
            interaction: {
              mode: 'index',
              intersect: false,
            },
            stacked: false,
            maintainAspectRatio: false,
            scales: {
              yAxes: [
                {
                  ticks: {
                    beginAtZero: true,
                  },
                },
              ],
            },
            legend: {
              labels: {
                fontSize: 32,
              },
            },
          }}
        />
      </div>
    </>
  )
}

export default LineChart