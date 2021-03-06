import React from "react";
import { Line } from "react-chartjs-2";
import styled from "styled-components";

const Chart = ({ inputData, type }) => {
  const data = {
    labels: inputData.yearMonth,
    datasets: [
      {
        data: inputData.count,
        fill: false,
        borderColor: type === "movie" ? "#4f60b8" : "#b84f55",
        tension: 0.1,
      },
    ],
  };
  const options = {
    plugins: {
      legend: {
        display: false,
      },
    },
    elements: {
      point: {
        // 그래프 꼭짓점 모양
        pointStyle: "circle",
        backgroundColor: type === "movie" ? "#4f60b8" : "#b84f55",
        radius: 5,
        hoverRadius: 10,
      },
    },
    scales: {
      x: {
        ticks: { color: `#ffffff` },
      },

      y: {
        ticks: { color: `#ffffff` },
      },
    },
  };

  return (
    <ChartBlock>
      <Line data={data} options={options} />
    </ChartBlock>
  );
};

const ChartBlock = styled.div`
  width: 100%;
  display: flex;
  align-items: center;
`;
export default Chart;
