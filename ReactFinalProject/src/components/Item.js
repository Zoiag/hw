import React from 'react';
import { Card } from 'react-bootstrap';

const Item = ({ item }) => {
    const coverImage = item.cover_i ? `https://covers.openlibrary.org/b/id/${item.cover_i}-M.jpg` : 'https://via.placeholder.com/150';
    return (
        <Card className="item">
            <Card.Img variant="top" src={coverImage} alt={item.title} />
            <Card.Body>
                <Card.Title>{item.title}</Card.Title>
                <Card.Text>
                    {item.author_name ? `Author: ${item.author_name.join(', ')}` : 'Author: Unknown'}
                </Card.Text>
                <Card.Text>
                    {item.first_publish_year ? `First Published: ${item.first_publish_year}` : 'Publication Year: Unknown'}
                </Card.Text>
            </Card.Body>
        </Card>
    );
};

export default Item;
