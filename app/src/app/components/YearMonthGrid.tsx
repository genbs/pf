"use client"

import { DataGrid, GridColDef } from "@mui/x-data-grid"

export type YearMonthGridData = {
	id: string | number
	year: string
	Jenuary: number
	February: number
	March: number
	April: number
	May: number
	June: number
	July: number
	August: number
	September: number
	October: number
	November: number
	December: number
}[]

interface YearMonthGridProps {
	data: YearMonthGridData
	showTotal?: boolean
}

export default function YearMonthGrid(props: YearMonthGridProps) {
	const columns: GridColDef[] = [
		{
			field: "year",
			headerName: "",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
			renderCell: params => {
				return <strong>{params.value}</strong>
			},
		},
		{
			field: "Jenuary",
			headerName: "Jenuary",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		},
		{
			field: "February",
			headerName: "February",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		},
		{
			field: "March",
			headerName: "March",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		},
		{
			field: "April",
			headerName: "April",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		},
		{
			field: "May",
			headerName: "May",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		},
		{
			field: "June",
			headerName: "June",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		},
		{
			field: "July",
			headerName: "July",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		},
		{
			field: "August",
			headerName: "August",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		},
		{
			field: "September",
			headerName: "September",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		},
		{
			field: "October",
			headerName: "October",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		},
		{
			field: "November",
			headerName: "November",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		},
		{
			field: "December",
			headerName: "December",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		},
	]

	let data = props.data

	if (props.showTotal) {
		columns.push({
			field: "total",
			headerName: "Total",
			sortable: false,
			resizable: false,
			editable: false,
			disableColumnMenu: true,
			flex: 1,
		})

		data = props.data.map(row => {
			const total =
				row.Jenuary +
				row.February +
				row.March +
				row.April +
				row.May +
				row.June +
				row.July +
				row.August +
				row.September +
				row.October +
				row.November +
				row.December
			return { ...row, total }
		})

		data.push({
			id: "total",
			year: "",
			Jenuary: data.reduce((acc, row) => acc + row.Jenuary, 0),
			February: data.reduce((acc, row) => acc + row.February, 0),
			March: data.reduce((acc, row) => acc + row.March, 0),
			April: data.reduce((acc, row) => acc + row.April, 0),
			May: data.reduce((acc, row) => acc + row.May, 0),
			June: data.reduce((acc, row) => acc + row.June, 0),
			July: data.reduce((acc, row) => acc + row.July, 0),
			August: data.reduce((acc, row) => acc + row.August, 0),
			September: data.reduce((acc, row) => acc + row.September, 0),
			October: data.reduce((acc, row) => acc + row.October, 0),
			November: data.reduce((acc, row) => acc + row.November, 0),
			December: data.reduce((acc, row) => acc + row.December, 0),
			// @ts-ignore
			total: data.reduce((acc, row) => acc + row.total, 0),
		})
	}

	return <DataGrid rows={data} columns={columns} hideFooter />
}
