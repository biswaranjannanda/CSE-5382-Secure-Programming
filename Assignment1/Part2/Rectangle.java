//Biswa Ranjan Nanda
//1001558251

public class Rectangle {

	private double length,width;

	public Rectangle() {
		length = 0;
		width = 0;
	}

	public Rectangle(double l,double w) {
		setLength(l);
		setWidth(w);
	}

	public double getLength() {
		return length;
	}

	public double getWidth() {
		return width;
	}

	public void setWidth(double w) {
		width = w;
	}

	public void setLength(double l) {
		length = l;
	}

	public String toString() {
		return "Length of the Rectangle : " + length + "\nWidth of the Rectangle : " + width;
	}

	public double area () {
		return length * width ;
	}

	public double perimeter() {
		return 2 * (length + width);
	}
}