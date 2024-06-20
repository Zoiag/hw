import React from 'react';
import { Form } from 'react-bootstrap';
import './YearFilter.scss';

const YearFilter = ({ setYear }) => (
    <Form className="year-filter">
        <Form.Group controlId="yearSelect">
            <Form.Label>Year</Form.Label>
            <Form.Control
                type="number"
                placeholder="Year"
                className="filter-input"
                onChange={(e) => setYear(e.target.value)}
            />
        </Form.Group>
    </Form>
);

export default YearFilter;
