"use client"

import YearMonthGrid, { YearMonthGridData } from "../components/YearMonthGrid"
import { Account, MONTHS, Transaction } from "../types"

interface YearExpensesProps {
	transactions: Transaction[]
	accounts: Account[]
}

export default function YearExpenses(props: YearExpensesProps) {
	const years = [2022, 2023]
	const map = getTransactionsYearMonthMap(
		props.transactions.filter(transaction => {
			const year = new Date(transaction.completed_date).getFullYear()
			return (
				transaction.type === "incoming" &&
				transaction.currency === "EUR" &&
				transaction.account_id === 1 &&
				years.includes(year)
			)
		})
	)

	// return YearMonthGridData
	const bancopostaIncoming = Object.keys(map).reduce((acc, year: string) => {
		const yearData = map[year]

		const row = {
			id: year,
			year,
			Jenuary: yearData["January"] ? sumTransactions(yearData["January"]) : 0,
			February: yearData["February"] ? sumTransactions(yearData["February"]) : 0,
			March: yearData["March"] ? sumTransactions(yearData["March"]) : 0,
			April: yearData["April"] ? sumTransactions(yearData["April"]) : 0,
			May: yearData["May"] ? sumTransactions(yearData["May"]) : 0,
			June: yearData["June"] ? sumTransactions(yearData["June"]) : 0,
			July: yearData["July"] ? sumTransactions(yearData["July"]) : 0,
			August: yearData["August"] ? sumTransactions(yearData["August"]) : 0,
			September: yearData["September"] ? sumTransactions(yearData["September"]) : 0,
			October: yearData["October"] ? sumTransactions(yearData["October"]) : 0,
			November: yearData["November"] ? sumTransactions(yearData["November"]) : 0,
			December: yearData["December"] ? sumTransactions(yearData["December"]) : 0,
		}
		acc.push(row)
		return acc
	}, [] as YearMonthGridData)

	return (
		<>
			<div>
				<h1>Incoming</h1>
				<YearMonthGrid data={bancopostaIncoming} showTotal />
			</div>
		</>
	)
}

function sumTransactions(transaction: Transaction[]): number {
	return transaction.reduce((acc, transaction) => acc + transaction.amount + transaction.fee, 0)
}

function getTransactionsYearMonthMap(transactions: Transaction[]): {
	[year: string]: { [month: string]: Transaction[] }
} {
	const yearMonthMap: { [year: string]: { [month: string]: Transaction[] } } = {}

	transactions.forEach(transaction => {
		const date = new Date(transaction.completed_date)
		const year = date.getFullYear() + ""
		const month = MONTHS[date.getMonth()]
		if (!yearMonthMap[year]) {
			yearMonthMap[year] = {}
		}

		if (!yearMonthMap[year][month]) {
			yearMonthMap[year][month] = []
		}

		yearMonthMap[year][month].push(transaction)
	})

	return yearMonthMap
}
