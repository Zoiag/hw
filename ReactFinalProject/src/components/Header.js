import React from 'react';
import { Navbar } from 'react-bootstrap';
import './Header.scss';

const Header = () => (
    <Navbar bg="dark" variant="dark" className="justify-content-center">
        <Navbar.Brand href="#home" className="text-center">Book Finder</Navbar.Brand>
    </Navbar>
);

export default Header;
